from enum import Enum, auto
import re
from preferences import prefs
from google_sheets import get_sheet


class Scale(Enum):
    LINEAR = auto()
    LINEAR_INVERT = auto()
    NONE = auto()


class GradeType(Enum):
    INTEGER = auto()
    NUMBER = auto()
    ALPHABETIC = auto()
    SET = auto()

class GradeScheme:
    def __init__(self, name=None, lower_bound=None, upper_bound=None, pass_bound=None, scale=None, gtype=None, gset=None):
        self.scale = scale
        self.gtype = gtype
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.pass_bound = pass_bound
        self.gset = gset
        self.name = name


grade_schemes = {
    'IB':GradeScheme(name='IB', lower_bound=1, upper_bound=7, pass_bound=3, scale=Scale.LINEAR, gtype=GradeType.INTEGER),
    'AP':GradeScheme(name='AP', lower_bound=1, upper_bound=5, pass_bound=3, scale=Scale.LINEAR, gtype=GradeType.INTEGER),
    'PERCENTAGE':GradeScheme(name='PERCENTAGE', lower_bound=0, upper_bound=100, pass_bound=60, scale=Scale.LINEAR, gtype=GradeType.NUMBER),
    'ALPHABETIC_WHOLE':GradeScheme(name='ALPHABETIC_WHOLE', lower_bound='F', upper_bound='A', pass_bound='C', scale=Scale.LINEAR_INVERT, gtype=GradeType.ALPHABETIC),
    'ALPHABETIC_HALF':GradeScheme(name='ALPHABETIC_HALF', scale=Scale.LINEAR, pass_bound='D', gtype=GradeType.SET,
                                  gset=['F', 'D-', 'D', 'D+', 'C-', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A', 'A+']),
    'ATL':GradeScheme(name='ATL', scale=Scale.LINEAR_INVERT, gtype=GradeType.SET, pass_bound='AP',
        gset=["EX", "ME", "AP", "DM"])
}


class GradeSet:
    operators = [
        ">=", "<=", ">", "<", "=="
    ]

    def __init__(self, scheme):
        if isinstance(scheme, GradeScheme): self.scheme = scheme
        elif isinstance(scheme, str) and scheme in grade_schemes: self.scheme = grade_schemes[scheme]

    def isnumeric(self):
        return self.scheme.gtype == GradeType.INTEGER or self.scheme.gtype == GradeType.NUMBER

    def is_valid(self, grade):
        if self.scheme.gtype == GradeType.INTEGER:
            if isinstance(grade, int) and self.scheme.lower_bound <= grade <= self.scheme.upper_bound:
                return True
            return False
        elif self.isnumeric():
            try:
                if self.scheme.lower_bound <= float(grade) <= self.scheme.upper_bound:
                    return True
                else:
                    return False
            except ValueError:
                return False
        elif self.scheme.gtype == GradeType.ALPHABETIC:
            if isinstance(grade, str) and len(grade) == 1 and str.isalpha(grade):
                if self.scheme.scale == Scale.LINEAR_INVERT:
                    return self.scheme.upper_bound <= grade <= self.scheme.lower_bound
                elif self.scheme.scale == Scale.LINEAR:
                    return self.scheme.upper_bound >= grade >= self.scheme.lower_bound
                return False
        elif self.scheme.gtype == GradeType.SET:
            return grade in self.scheme.gset
        return False

    def validate(self, *args):
        return not (False in [self.is_valid(a) for a in args])

    def is_passing(self, grade):
        if self.scheme is None: return True
        if not self.validate(grade, self.scheme.pass_bound): return False
        return self.compare(grade, self.scheme.pass_bound, ">=")

    def compare(self, a, b, operator):
        # Map all accepted operators to lambda functions, as inputs will always be numerical (either being numeric values of indices of values in a set)
        if self.scheme.scale == Scale.LINEAR:
            operator_set = {
                ">=": (lambda a1, a2: a1 >= a2),
                ">": (lambda a1, a2: a1 > a2),
                "<": (lambda a1, a2: a1 < a2),
                "<=": (lambda a1, a2: a1 <= a2),
                "==": (lambda a1, a2: a1 == a2)
            }
        else:
            # Switch operator lambdas for < and > families, as flipped list means flipped compares of indices
            operator_set = {
                "<=": (lambda a1, a2: a1 >= a2),
                "<": (lambda a1, a2: a1 > a2),
                ">": (lambda a1, a2: a1 < a2),
                ">=": (lambda a1, a2: a1 <= a2),
                "==": (lambda a1, a2: a1 == a2)
            }

        if self.isnumeric() and (isinstance(a, str) or isinstance(b, str)):
            if self.scheme.gtype == GradeType.INTEGER:
                if isinstance(a, str) and str.isdigit(a):
                    a = int(a)
                if isinstance(b, str) and str.isdigit(b):
                    b = int(b)
            elif self.scheme.gtype == GradeType.NUMBER:
                if isinstance(a, str):
                    try:
                        a = float(a)
                    except ValueError:
                        return False
                if isinstance(b, str):
                    try:
                        b = float(b)
                    except ValueError:
                        return False

        if not self.validate(a, b) or not operator in operator_set:
            return False
        if self.isnumeric() or self.scheme.gtype == GradeType.ALPHABETIC:
            return operator_set[operator](a, b)  # Simply direct compare numeric items
        elif self.scheme.gtype == GradeType.SET:
            return operator_set[operator](self.scheme.gset.index(a), self.scheme.gset.index(
                b))  # Grab indices of a linear set to compare i.e. in set ['C', 'B', 'A'], index('A') > index('C')

        return False

    @staticmethod
    def tokenize(tstr):
        # split but keep tokens by using capture group on operators joined with or i.e. (>=|<=|>|<|==) which keeps matched ranges
        return [elem.strip() for elem in re.split(f"({'|'.join(GradeSet.operators)})", tstr)]


def mean(l):
    return sum(l) / len(l)


if __name__ == '__main__':
    g = GradeSet(GradeScheme())
    test_grades = {'Test 1': '6', 'Test 2': '7', 'Grade 3': '7', 'Grade 4': '7', 'Grade 5': '7'}
    comp_str = GradeSet.tokenize("1 <= 2")

    if len(comp_str) == 3:
        arg1, arg2, op = comp_str[0], comp_str[2], comp_str[1]
        if arg1 in test_grades: arg1 = test_grades[arg1]
        if arg2 in test_grades: arg2 = test_grades[arg2]
        print(g.compare(arg1, arg2, op))
    else:
        print("Invalid operator string")

    # grade_rules = get_sheet(prefs.get_pref('report_sheet'), "{}!A1:Z1000".format('Grade Rules'), mode='COLUMNS').get('values')
    # GradeScheme[grade_rules[0][0]]

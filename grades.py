from enum import Enum, auto
import re
from preferences import prefs
from sheets import get_sheet
from copy import deepcopy

class GradeScale(Enum):
    INCREASING = ("I")
    DECREASING = ("D")
    BINARY = ("B")
    NONE = ('')

    def __init__(self, text):
        self.text = text
class GradeType(Enum):
    INTEGER = ("I")
    NUMBER = ("N")
    ALPHABETIC = ("A")
    SET = ("S")
    MAP = ("M")
    NONE = ('')

    @staticmethod
    def is_numeric(gt): return gt == GradeType.INTEGER or gt == GradeType.NUMBER
    def __init__(self, text):
        self.text = text

def stringToGradeType(s):
    gtsm =  {gt.text:gt for gt in GradeType}
    if s in gtsm: return gtsm[s]
    else: return gtsm['']

def stringToGradeScale(s):
    gssm = {gs.text:gs for gs in GradeScale}
    if s in gssm: return gssm[s]
    else: return gssm['']


class GradeScheme:
    def __init__(self, name=None, lower_bound=None, upper_bound=None, pass_bound=None, gscale=None, gtype=None, gset=None):
        self.name = name
        self.gscale = gscale
        self.gtype = gtype
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.pass_bound = pass_bound
        if gset is not None:
            self.gset = [g.lower() if isinstance(g, str) else g for g in gset if isinstance(g, str)]
        else:
            self.gset = None


default_schemes = {
    'IB':GradeScheme(name='IB', lower_bound=1, upper_bound=7, pass_bound=3, gscale=GradeScale.INCREASING, gtype=GradeType.INTEGER),
    'AP':GradeScheme(name='AP', lower_bound=1, upper_bound=5, pass_bound=3, gscale=GradeScale.INCREASING, gtype=GradeType.INTEGER),
    'PERCENTAGE':GradeScheme(name='PERCENTAGE', lower_bound=0, upper_bound=100, pass_bound=60, gscale=GradeScale.INCREASING, gtype=GradeType.NUMBER),
    'ALPHABETIC_WHOLE':GradeScheme(name='ALPHABETIC_WHOLE', lower_bound='F', upper_bound='A', pass_bound='C', gscale=GradeScale.DECREASING, gtype=GradeType.ALPHABETIC),
    'ALPHABETIC_HALF':GradeScheme(name='ALPHABETIC_HALF', gscale=GradeScale.INCREASING, pass_bound='D', gtype=GradeType.SET,
                                  gset=['F', 'D-', 'D', 'D+', 'C-', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A', 'A+']),
    'MS':GradeScheme(name='MS', gscale=GradeScale.DECREASING, gtype=GradeType.SET, pass_bound='AP', gset=["EX", "ME", "AP", "DM"]),
    'ATL': GradeScheme(name='ATL', gscale=GradeScale.INCREASING, gtype=GradeType.SET, pass_bound='S', gset=["R", "S", "C"]),
}

grade_schemes = deepcopy(default_schemes)

class GradeSet:
    operators = [
        ">=", "<=", ">", "<", "==", "!="
    ]

    def __init__(self, scheme):
        if isinstance(scheme, GradeScheme): self.scheme = scheme
        elif isinstance(scheme, str) and scheme in grade_schemes: self.scheme = grade_schemes[scheme]
        else: self.scheme = None

    def isnumeric(self): return self.scheme.gtype == GradeType.INTEGER or self.scheme.gtype == GradeType.NUMBER
    def is_valid(self, grade):
        if self.scheme is None:
            return False
        elif self.scheme.gtype == GradeType.INTEGER:
            if isinstance(grade, str):
                try:
                    grade = int(grade)
                except ValueError:
                    return False
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
                if self.scheme.scale == GradeScale.DECREASING:
                    return self.scheme.upper_bound <= grade <= self.scheme.lower_bound
                elif self.scheme.scale == GradeScale.INCREASING:
                    return self.scheme.upper_bound >= grade >= self.scheme.lower_bound
                return False
        elif self.scheme.gtype == GradeType.SET:
            return grade.lower() in self.scheme.gset
        elif self.scheme.gtype == GradeType.MAP:
            return grade.lower() in self.scheme.gset
        return False

    def validate(self, *args): return not (False in [self.is_valid(a) for a in args])

    def is_passing(self, grade):
        if self.scheme is None: return True
        if not self.validate(grade, self.scheme.pass_bound): return False
        return self.compare(grade, self.scheme.pass_bound, ">=")

    def compare(self, a, b, operator):
        flip = not (self.scheme.gscale == GradeScale.DECREASING)
        operator_set = {
            ">=": (lambda a1, a2: a1 >= a2 if flip else a1 <= a2),
            ">": (lambda a1, a2: a1 > a2 if flip else a1 < a2),
            "<": (lambda a1, a2: a1 < a2 if flip else a1 > a2),
            "<=": (lambda a1, a2: a1 <= a2 if flip else a1 >= a2),
            "==": (lambda a1, a2: a1 == a2),
            "!=":(lambda a1, a2: a1 != a2)
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
            return operator_set[operator](self.scheme.gset.index(a), self.scheme.gset.index(b))  # Grab indices of a linear set to compare i.e. in set ['C', 'B', 'A'], index('A') > index('C')
        return False

    def evaluate(self, grades, rule):
        rule_parts = self.tokenize(rule)
        if len(rule_parts) == 3:
            arg1, arg2, op = rule_parts[0], rule_parts[2], rule_parts[1]
            keys_lower = {k.lower():v for k,v in grades.items()}
            if arg1 in keys_lower: arg1 = keys_lower[arg1]['grade']
            if arg2 in keys_lower: arg2 = keys_lower[arg2]['grade']
            return self.compare(arg1, arg2, op)
        return False

    @staticmethod
    def tokenize(tstr):
        # split but keep tokens by using capture group on operators joined with or i.e. (>=|<=|>|<|==|!=) which keeps matched ranges
        return [elem.strip().lower() for elem in re.split(f"({'|'.join(GradeSet.operators)})", tstr)]

def load_grades(grade_tabs=None):
    global grade_schemes
    global default_schemes

    grade_schemes = deepcopy(default_schemes)
    if grade_tabs:
        for tab in grade_tabs:
            grade_rules = get_sheet(prefs.get_pref('report_sheet'), "{}!A1:Z1000".format(tab), mode='COLUMNS').get('values')
            if grade_rules:
                for s in grade_rules:
                    scheme_data = ["","",""]

                    for i, part in enumerate(r.strip() for r in re.split("[$|]", s[0])): scheme_data[i] = part
                    scheme_arguments = list(filter(None, s[1:]))

                    if len(scheme_arguments) > 0:
                        scheme_data[1] = stringToGradeScale(scheme_data[1])
                        if scheme_data[1] == GradeScale.NONE: scheme_data[1] = GradeScale.DECREASING

                        scheme_data[2] = stringToGradeType(scheme_data[2])
                        if scheme_data[2] == GradeType.NONE or scheme_data[2] == GradeType.SET:
                            if scheme_data[2] == GradeType.NONE: scheme_data[2] = GradeType.SET
                            grade_schemes[scheme_data[0]] = GradeScheme(gscale=scheme_data[1],
                                                                        gtype=scheme_data[2],
                                                                        gset=scheme_arguments)
                        else:
                            if GradeType.is_numeric(scheme_data[2]):
                                try:
                                    ub = int(scheme_arguments[0]) if scheme_arguments == GradeType.INTEGER else float(scheme_arguments[0])
                                    if len(scheme_arguments) == 1:
                                        pb = 0
                                        lb = 0
                                    elif len(scheme_arguments) == 2:
                                        pb, lb = int(scheme_arguments[1]) if scheme_arguments == GradeType.INTEGER else float(scheme_arguments[1])
                                    else:
                                        pb = int(scheme_arguments[1]) if scheme_arguments == GradeType.INTEGER else float(scheme_arguments[1])
                                        lb = int(scheme_arguments[2]) if scheme_arguments == GradeType.INTEGER else float(scheme_arguments[2])
                                    grade_schemes[scheme_data[0]] = GradeScheme(gscale=scheme_data[1],
                                                                                gtype=scheme_data[2],
                                                                                lower_bound=lb,
                                                                                upper_bound=ub,
                                                                                pass_bound=pb)
                                except ValueError:
                                    print("Invalid member data")
                            elif scheme_arguments[2] == GradeType.ALPHABETIC:
                                pass
if __name__ == "__main__":
    print([gt for gt in GradeType])
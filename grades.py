from enum import Enum, auto
import re

class Scale(Enum):
    LINEAR = auto()
    LINEAR_INVERT = auto()
    NONE = auto()

class GradeType(Enum):
    INTEGER = auto()
    NUMBER = auto()
    ALPHABETIC = auto()
    SET = auto()

class GradeScheme(Enum):
    IB = {
        'lower_bound':1,
        'upper_bound':7,
        'pass_bound': 3,
        'scale':Scale.LINEAR,
        'type':GradeType.INTEGER
    }

    AP = {
        'lower_bound':1,
        'upper_bound':5,
        'pass_bound': 3,
        'scale':Scale.LINEAR,
        'type':GradeType.INTEGER
     }

    PERCENTAGE = {
        'lower_bound':0,
        'upper_bound':100,
        'pass_bound': 60,
        'scale':Scale.LINEAR,
        'type':GradeType.NUMBER
    }

    ALPHABETICAL_WHOLE = {
        'lower_bound':'F',
        'upper_bound':'A',
        'pass_bound':'C',
        'scale':Scale.LINEAR_INVERT,
        'type':GradeType.ALPHABETIC
    }

    ALPHABETICAL_HALF = {
        'set':['F', 'D-', 'D', 'D+', 'C-', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A', 'A+'],
        'pass_bound': 'A+',
        'scale':Scale.LINEAR,
        'type':GradeType.SET
    }

    TIER_LIST = {
        'set':['F', 'E', 'D', 'C', 'B', 'A', 'S', 'SS'],
        'pass_bound':'C',
        'scale':Scale.LINEAR,
        'type':GradeType.SET
    }

    ATL = {
        'set':["EX", "ME", "AP", "DM"],
        'pass_bound':'AP',
        'scale':Scale.LINEAR_INVERT,
        'type':GradeType.SET
    }

    def isnumeric(self):
        return self.value['type'] == GradeType.INTEGER or self.value['type'] == GradeType.NUMBER

class GradeSet:
    operators = [
        ">=", "<=", ">", "<", "=="
    ]

    def __init__(self, scheme = GradeScheme.ALPHABETICAL_HALF):
        self.scheme = scheme
        self.s = self.scheme.value

    def is_valid(self, grade):
        if self.s['type'] == GradeType.INTEGER:
            if isinstance(grade, int) and self.s['lower_bound'] <= grade <= self.s['upper_bound']:
                return True
            return False
        elif self.scheme.isnumeric():
            try:
                if self.s['lower_bound'] <= float(grade) <= self.s['upper_bound']:
                    return True
                else:
                    return False
            except ValueError:
                return False
        elif self.s['type'] == GradeType.ALPHABETIC:
           if isinstance(grade, str) and len(grade) == 1 and str.isalpha(grade):
               if self.s['scale'] == Scale.LINEAR_INVERT:
                   return self.s['upper_bound'] <= grade <= self.s['lower_bound']
               elif self.s['scale'] == Scale.LINEAR:
                   return self.s['upper_bound'] >= grade >= self.s['upper_bound']
               return False
        elif self.s['type'] == GradeType.SET:
            return grade in self.s['set']
        return False

    def validate(self, *args):
        return not (False in [self.is_valid(a) for a in args])

    def is_passing(self, grade):
        if not 'pass_bound' in self.s: return True
        if not self.validate(grade, self.s['pass_bound']): return False
        return self.compare(grade, self.s['pass_bound'], ">=")

    def compare(self, a, b, operator):
        #Map all accepted operators to lambda functions, as inputs will always be numerical (either being numeric values of indices of values in a set)
        if self.s['scale'] == Scale.LINEAR:
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
                "<=":(lambda a1, a2: a1 >= a2),
                "<": (lambda a1, a2: a1 > a2),
                ">": (lambda a1, a2: a1 < a2),
                ">=": (lambda a1, a2: a1 <= a2),
                "==": (lambda a1, a2: a1 == a2)
            }

        if self.scheme.isnumeric() and (isinstance(a, str) or isinstance(b, str)):
            if self.s['type'] == GradeType.INTEGER:
                if isinstance(a, str) and str.isdigit(a):
                    a = int(a)
                if isinstance(b, str) and str.isdigit(b):
                    b = int(b)
            elif self.s['type'] == GradeType.NUMBER:
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
        if self.scheme.isnumeric() or self.s['type'] == GradeType.ALPHABETIC:
            return operator_set[operator](a, b) #Simply direct compare numeric items
        elif self.s['type'] == GradeType.SET:
            return operator_set[operator](self.s['set'].index(a), self.s['set'].index(b)) #Grab indices of a linear set to compare i.e. in set ['C', 'B', 'A'], index('A') > index('C')


        return False

    @staticmethod
    def tokenize(tstr):
        #split but keep tokens by using capture group on operators joined with or i.e. (>=|<=|>|<|==) which keeps matched ranges
        return [elem.strip() for elem in re.split(f"({'|'.join(GradeSet.operators)})", tstr)]


def mean(l):
    return sum(l)/len(l)

if __name__ == '__main__':
    g = GradeSet(GradeScheme.PERCENTAGE)
    test_grades = {'Test 1': '6', 'Test 2': '7', 'Grade 3': '7', 'Grade 4': '7', 'Grade 5': '7'}
    comp_str = GradeSet.tokenize("10 >= 6")

    if len(comp_str) == 3:
        arg1, arg2, op = comp_str[0], comp_str[2], comp_str[1]
        if arg1 in test_grades: arg1 = test_grades[arg1]
        if arg2 in test_grades: arg2 = test_grades[arg2]
        print(g.compare(arg1, arg2, op))
    else:
        print("Invalid operator string")





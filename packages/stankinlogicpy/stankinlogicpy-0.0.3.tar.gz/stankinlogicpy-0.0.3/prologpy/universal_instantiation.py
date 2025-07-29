from model import UniversalQuantifier
from substitute import substitute

def universalInstantiation(universal, term):
    if isinstance(universal, UniversalQuantifier):
        # Заменяем все вхождения переменной на терм
        return substitute(universal.formula, universal.variable, term)
    else:
        raise ValueError("Universal Instantiation can only be applied to universal quantifiers")
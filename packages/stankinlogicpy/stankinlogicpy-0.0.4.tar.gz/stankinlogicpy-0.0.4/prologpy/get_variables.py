from itertools import product
from model import *
def getVariables(formula):
    """Рекурсивно собираем все переменные в формуле."""
    if isinstance(formula, AtomicFormula):
        return {formula.name}
    elif isinstance(formula, Negation):
        return getVariables(formula.formula)
    elif isinstance(formula, (Conjunction, Disjunction, Implication)):
        return getVariables(formula.left) | getVariables(formula.right)
    else:
        return set()
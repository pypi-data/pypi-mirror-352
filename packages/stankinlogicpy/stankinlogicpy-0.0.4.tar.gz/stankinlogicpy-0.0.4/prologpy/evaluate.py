from model import *

def evaluate(formula, interpretation):
    """Вычисление значения формулы для данной интерпретации."""
    if isinstance(formula, AtomicFormula):
        return interpretation[formula.name]
    elif isinstance(formula, Negation):
        return not evaluate(formula.formula, interpretation)
    elif isinstance(formula, Conjunction):
        return evaluate(formula.left, interpretation) and evaluate(formula.right, interpretation)
    elif isinstance(formula, Disjunction):
        return evaluate(formula.left, interpretation) or evaluate(formula.right, interpretation)
    elif isinstance(formula, Implication):
        return (not evaluate(formula.left, interpretation)) or evaluate(formula.right, interpretation)
    else:
        raise ValueError(f"Unknown formula type: {type(formula)}")
from model import Quantifier, Negation, Conjunction, Disjunction, Implication

def toPnf(formula):
    if isinstance(formula, Quantifier):
        # Если формула уже начинается с квантора, рекурсивно обрабатываем подформулу
        formula.formula = toPnf(formula.formula)
        return formula
    elif isinstance(formula, Negation):
        # Обрабатываем отрицание
        return Negation(toPnf(formula.formula))
    elif isinstance(formula, (Conjunction, Disjunction, Implication)):
        # Обрабатываем бинарные связки
        formula.left = toPnf(formula.left)
        formula.right = toPnf(formula.right)
        return formula
    else:
        # Атомарные формулы и другие случаи
        return formula
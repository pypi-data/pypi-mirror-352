from model import AtomicFormula, Negation, Conjunction, Disjunction, Implication, Predicate, Quantifier

def substitute(formula, variable, term):
    if isinstance(formula, AtomicFormula):
        # Заменяем переменную в аргументах предиката
        new_args = [term if arg == variable else arg for arg in formula.predicate.args]
        return AtomicFormula(Predicate(formula.predicate.name, new_args))
    elif isinstance(formula, Negation):
        return Negation(substitute(formula.formula, variable, term))
    elif isinstance(formula, (Conjunction, Disjunction, Implication)):
        return formula.__class__(
            substitute(formula.left, variable, term),
            substitute(formula.right, variable, term)
        )
    elif isinstance(formula, Quantifier):
        if formula.variable == variable:
            # Если переменная связана квантором, подстановка не производится
            return formula
        else:
            return formula.__class__(formula.variable, substitute(formula.formula, variable, term))
    else:
        return formula
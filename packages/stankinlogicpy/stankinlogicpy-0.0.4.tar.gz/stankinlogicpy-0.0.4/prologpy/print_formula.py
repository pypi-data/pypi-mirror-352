from model import *

def print_formula(formula):
    if isinstance(formula, UniversalQuantifier):
        return f"∀{formula.variable.name} ({print_formula(formula.formula)})"
    elif isinstance(formula, Implication):
        return f"({print_formula(formula.left)} → {print_formula(formula.right)})"
    elif isinstance(formula, AtomicFormula):
        return f"{formula.predicate.name}({', '.join(arg.name for arg in formula.predicate.args)})"
from print_formula import *
from model import *
# Создание формулы: ∀x (P(x) → Q(x))
x = Variable('x')
P = Predicate('P', [x])
Q = Predicate('Q', [x])
implication = Implication(AtomicFormula(P), AtomicFormula(Q))
universal = UniversalQuantifier(x, implication)
print(print_formula(universal)) 
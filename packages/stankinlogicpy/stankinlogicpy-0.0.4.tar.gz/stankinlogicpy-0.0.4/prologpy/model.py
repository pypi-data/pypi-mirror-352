class Term:
    pass

class Constant(Term):
    def __init__(self, name):
        self.name = name

class Variable(Term):
    def __init__(self, name):
        self.name = name

class Function(Term):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class Predicate:
    def __init__(self, name, args):
        self.name = name
        self.args = args

class Formula:
    pass

class AtomicFormula(Formula):
    def __init__(self, predicate):
        self.predicate = predicate

class Negation(Formula):
    def __init__(self, formula):
        self.formula = formula

class Conjunction(Formula):
    def __init__(self, left, right):
        self.left = left
        self.right = right

class Disjunction(Formula):
    def __init__(self, left, right):
        self.left = left
        self.right = right

class Implication(Formula):
    def __init__(self, left, right):
        self.left = left
        self.right = right

class Quantifier(Formula):
    pass

class UniversalQuantifier(Quantifier):
    def __init__(self, variable, formula):
        self.variable = variable
        self.formula = formula

class ExistentialQuantifier(Quantifier):
    def __init__(self, variable, formula):
        self.variable = variable
        self.formula = formula
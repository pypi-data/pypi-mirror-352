from model import Implication

def modusPonens(implication, antecedent):
    if isinstance(implication, Implication) and implication.left == antecedent:
        return implication.right
    else:
        raise ValueError("Modus Ponens cannot be applied: invalid input formulas")
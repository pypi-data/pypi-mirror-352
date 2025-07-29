from model import Variable, Function

def unify(term1, term2, substitution=None):
    if substitution is None:
        substitution = {}
    if term1 == term2:
        return substitution
    elif isinstance(term1, Variable):
        return unify_variable(term1, term2, substitution)
    elif isinstance(term2, Variable):
        return unify_variable(term2, term1, substitution)
    elif isinstance(term1, Function) and isinstance(term2, Function):
        if term1.name != term2.name or len(term1.args) != len(term2.args):
            return None
        for arg1, arg2 in zip(term1.args, term2.args):
            substitution = unify(arg1, arg2, substitution)
            if substitution is None:
                return None
        return substitution
    else:
        return None

def unify_variable(variable, term, substitution):
    if variable in substitution:
        return unify(substitution[variable], term, substitution)
    elif term in substitution:
        return unify(variable, substitution[term], substitution)
    else:
        substitution[variable] = term
        return substitution
from get_variables import *
from generate_interpretations import *
from evaluate import *

def is_satisfiable(formula):
    """Проверка выполнимости формулы."""
    variables = list(getVariables(formula))
    for interpretation in generatInterpretations(variables):
        if evaluate(formula, interpretation):
            return True
    return False
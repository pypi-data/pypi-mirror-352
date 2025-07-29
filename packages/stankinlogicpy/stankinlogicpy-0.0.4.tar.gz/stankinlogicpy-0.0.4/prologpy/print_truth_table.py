from generate_interpretations import *
from get_variables import *
from evaluate import*

def print_truth_table(formula):
    """Вывод таблицы истинности для формулы."""
    variables = list(getVariables(formula))
    print(" | ".join(variables + ["Formula"]))
    print("-" * (len(variables) * 4 + 10))
    for interpretation in generatInterpretations(variables):
        values = [str(interpretation[var]) for var in variables]
        result = evaluate(formula, interpretation)
        print(" | ".join(values + [str(result)]))
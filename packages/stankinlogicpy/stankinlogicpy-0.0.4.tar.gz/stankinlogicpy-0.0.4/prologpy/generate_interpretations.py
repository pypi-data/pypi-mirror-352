from itertools import product

def generatInterpretations(variables):
    """Генерация всех возможных интерпретаций для переменных."""
    for values in product([False, True], repeat=len(variables)):
        yield dict(zip(variables, values))
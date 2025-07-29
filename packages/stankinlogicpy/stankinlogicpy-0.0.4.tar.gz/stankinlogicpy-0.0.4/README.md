# Библиотека для работы с предикатной логикой первого порядка

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](https://opensource.org/licenses/MIT)

Библиотека предоставляет инструменты для работы с предикатной логикой первого порядка, включая синтаксический анализ, преобразование и проверку выполнимости логических формул. Также поддерживается создание таблиц истинности для пропозициональной логики.

---

## Установка

Для установки библиотеки используйте `pip`:

```bash
pip install predicate_logic
```

## Основные возможности

- **Синтаксический анализ логических формул**:
  - Поддержка атомарных формул, кванторов, логических связок.

- **Преобразование формул**:
  - Приведение к нормальным формам (например, предваренная нормальная форма).

- **Проверка выполнимости**:
  - Оценка формул на заданных интерпретациях.

- **Таблицы истинности**:
  - Генерация таблиц истинности для пропозициональных формул.

## Быстрый старт

### 1. Создание и оценка формул

```python
from predicate_logic.core.parser import AtomicFormula, Predicate, Constant, Conjunction
from predicate_logic.core.evaluator import evaluate

# Создаем атомарные формулы
P_a = AtomicFormula(Predicate('P', [Constant('a')]))
Q_a_b = AtomicFormula(Predicate('Q', [Constant('a'), Constant('b')]))

# Создаем формулу: P(a) ∧ Q(a, b)
formula = Conjunction(P_a, Q_a_b)

# Пример интерпретации
interpretation = {
    'P': lambda x: x == 'a',  # Предикат P(x) истинен, если x == 'a'
    'Q': lambda x, y: x == y,  # Предикат Q(x, y) истинен, если x == y
    'constants': {'a': 'a', 'b': 'b'}  # Константы
}

# Оценка формулы
result = evaluate(formula, interpretation)
print("Результат оценки формулы:", result)
```
### 2. Таблицы истинности для пропозициональной логики

```python
from predicate_logic.truth_tables import TruthTable

# Пример использования
variables = ['A', 'B']
expression = "(A and B) or (not C)"
truth_table = TruthTable.create(variables, expression)
print(truth_table)
```

## Авторы

- [Муса](https://github.com/MosesAliev)

---

## Обратная связь

Если у вас есть вопросы или предложения, пожалуйста, создайте свяжитесь со мной по электронной почте: [aliev.musa.yol@gmail.com](mailto:aliev.musa.yo@gmail.com).

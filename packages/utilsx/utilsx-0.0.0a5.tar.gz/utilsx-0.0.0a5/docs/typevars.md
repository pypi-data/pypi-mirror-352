# 🇹 [Type variables](https://docs.python.org/3/library/typing.html#typing.TypeVar)

A collection of reusable type variables for your own type-safe generic utilities.

These aliases help clarify intent in your function signatures
and ensure consistent typing behavior across your codebase.

### `T`

A generic, unconstrained type variable.
Use this when the input and output **match in type**,
while allowing **any concrete type** as input.

``` py title="t_var.py" hl_lines="3 6"
from typing import Iterable

from utilsx.types import T


def first_item(items: Iterable[T]) -> T:
    for item in items:
        return item
    raise ValueError("Empty iterable")

first_item(["a", "b", "c"])  # str
first_item([1, 2, 3])        # int
```

This ensures the return type matches the input collection’s element type.

### `NumberT`

Useful in contexts like [`T`](#t), but when you want to limit the type to `float`
or its parents.

``` py title="number_t.py" hl_lines="3 6 14"
from typing import Iterable

from utilsx.types import NumberT


def average(values: Iterable[NumberT]) -> float:
    values = list(values)
    if not values:
        raise ValueError("Cannot compute average of empty list")
    return sum(values) / len(values)

average([10, 20, 30])    # OK: list of ints
average([1.5, 2.5, 3.0]) # OK: list of floats
average(["a", "b"])      # ❌ type checker will flag this
```

# ⛔ Exceptions

Utilities to help enrich exception messages.

### [`hint_if_extra_uninstalled`][utilsx.exceptions.hint_if_extra_uninstalled]

When developing a package with optional extras,
a good practice involves guiding users on how to install the required dependencies
if they attempt to import a feature without the corresponding extra.

Check out this example from UtilsX itself, particularly the `utils.pandas` module:

```py hl_lines="5-9"
"""Utilities for enhancing your Pandas workflows."""

from utilsx.exceptions import hint_if_extra_uninstalled as _hint_if_extra_uninstalled

_hint_if_extra_uninstalled(
    required_modules=frozenset(("pandas",)),
    extra_name="pandas",
    package_name="utilsx",
)

# This import should be after the dependency group check logic.
from ._missing import *  # noqa: E402
```

Note:

1. The import statement renames the helper function to a private identifier
`_hint_if_extra_uninstalled` so that it doesn't appear
in IDE auto-complete for users of `utilsx.pandas`.
1. Wildcard imports from submodules follow the hint function
ensuring the optional `utilsx[pandas]` extra gets validated before exposing public symbols.

### [`prohibit_negative_values`][utilsx.exceptions.prohibit_negative_values]

Suppose you process a list of daily sales amounts
that must never contain negative values, as they represent revenue:

``` py title="manual.py" hl_lines="5-6"
# Daily sales data
sales = [1200.0, 1500.5, -300.0, 1100.0]

# Manual check for negatives
if any(sale < 0 for sale in sales):
    raise ValueError("Sales data contains negative values")
```

This check remains straightforward but forces you to repeat the same pattern
wherever you enforce non-negativity, cluttering your code.

Use UtilsX to make this validation clear and reusable:

``` py title="with_utilsx.py" hl_lines="1 6-7"
from utilsx import prohibit_negative_values

# Daily sales data
sales = [1200.0, 1500.5, -300.0, 1100.0]

prohibit_negative_values(sales)
# ValueError: Negative values are prohibited
```

With `prohibit_negative_values`, you express your intent directly,
improving readability and reducing boilerplate in data validation steps.

By default, it raises `ValueError("Negative values are prohibited")`, but both
exception class and the message are configurable through function arguments.

### [`raise_key_error_with_suggestions`][utilsx.exceptions.raise_key_error_with_suggestions]

Suppose you look up car models in a catalog and want to provide helpful feedback
when a user queries a missing model, suggesting alternatives to reduce frustration:

``` py title="plain_key_error.py" hl_lines="9 13"
car_catalog = {
    "Toyota": ["Camry", "Corolla", "Prius"],
    "Honda": ["Civic", "Accord", "CR-V"],
    "Ford": ["F-150", "Mustang", "Explorer"],
}

def get_car_models(brand):
    if brand not in car_catalog:
        raise KeyError(f"Car brand {brand} not found.")
    return car_catalog[brand]

get_car_models("Toyta")
# KeyError: Car brand Toyta not found.
```

The error message provides no guidance or suggestions,
leaving users to guess correct brand names and slowing down debugging or user input.

Use UtilsX to enhance your error reporting:

``` py title="key_error_with_suggestion.py" hl_lines="1 11-16 20-21"
from utilsx import raise_key_error_with_suggestions

car_catalog = {
    "Toyota": ["Camry", "Corolla", "Prius"],
    "Honda": ["Civic", "Accord", "CR-V"],
    "Ford": ["F-150", "Mustang", "Explorer"],
}

def get_car_models(brand):
    if brand not in car_catalog:
        raise_key_error_with_suggestions(
            attempted_key=brand,
            existing_keys=car_catalog.keys(),
            object_name="car brand",
            attribute_name="name",
        )
    return car_catalog[brand]

get_car_models("Toyta")
# KeyError: Car brand with name Toyta not found.
# Did you mean one of these instead: Toyota, Honda?
```

`raise_key_error_with_suggestions` improves user experience by offering actionable hints,
helping users correct typos or misunderstandings quickly.

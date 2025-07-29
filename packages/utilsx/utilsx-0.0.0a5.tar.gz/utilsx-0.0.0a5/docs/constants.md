# 🪨 Constants

Common real-world constants for you to reuse across your project.

## Numbers

Commonly used literal numbers:

- `ONE`
- `TWO`
- `TEN`
- `HUNDRED`
- `THOUSAND`
- `MILLION`
- `BILLION`
- `TRILLION`

Besides helping avoid duplication of
[magic numbers](https://code-basics.com/languages/python/lessons/magic-numbers) in your code,
using these constants protects from typos involving missing / extra `0` in magic numbers.

Example:

``` py title="bad_practice.py"
revenue = 2819920021

# The number below has a missing zero - how long would it take for you to spot?
revenue_billions = revenue / 100000000
```

Do instead:

``` py title="good_practice.py"
from utilsx import BILLION

revenue = 2819920021
revenue_billions = revenue / BILLION
```

!!! tip "You can simplify conversion to thousands or millions even further"

    Check out [`convert_number_to_units`](math.md#convert_number_to_units)
    utility from **math** part of UtilsX for a shorthand function.

!!! tip "The built-in `math` module provides constants like `pi` and `e`"

    See full list [here](https://docs.python.org/3/library/math.html#constants).
    UtilsX does not re-define them, and encourages you to import them from `math`.

## Physics

UtilsX provides a few constants representing common mass and volume ratios:

- `GAL_TO_LITER` and `LITER_TO_GAL`
- `GAL_TO_OZ` and `OZ_TO_GAL`
- `LBS_TO_KG` and `KG_TO_LBS`

Like numeric constraints, this set fights against duplicated magic numbers in codebases.

Moreover, inconsistency here directly makes calculations imprecise:

``` py title="bad_practice.py" hl_lines="3 7"
# Work of one developer
production_kg = 500
production_lbs = production_kg * 2.205

# Work of another developer
consumption_lbs = 1000
consumption_kg = consumption_lbs * (1 / 2.20462)
```

A conversion ratio shouldn't appear as `2.205` in one part of the codebase, and `2.20462` in another.

Do instead:

``` py title="good_practice.py"
from utilsx import KG_TO_LBS, LBS_TO_KG

# Work of one developer
production_kg = 500
production_lbs = production_kg * KG_TO_LBS

# Work of another developer
consumption_lbs = 1000
consumption_kg = consumption_lbs * LBS_TO_KG
```

!!! note "You may also use [SciPy's `constants` module](https://docs.scipy.org/doc/scipy/reference/constants.html#)"

    For deep scientific projects, likely it would be more suitable.

    UtilsX, however:

    - Is more lightweight: does not bring whole SciPy (and NumPy as its transitive dependency) to your venv.
    - Uses more explicit names: e.g., `KG_TO_LBS` vs `pound` in SciPy.
    - Defines constants missing in SciPy: like `GAL_TO_OZ`, while SciPy only provides gallon-to-cubic-meter ratios.

For unit conversion ratios, UtilsX follows the following naming convention:

> Constants follow the `A_TO_B` naming convention, such that a value in units `A`
> **multiplied** by `A_TO_B` becomes the same amount in units `B`.

!!! info "Why this convention?"

    In early versions, for instance, `KG_TO_LBS` was called `LBS_IN_KG`.

    That name is ambiguous because can be interpreted both as:

    - How many lbs is there in 1 kg? (~2.2)
    - How many kg would it take to represent 1 lbs? (~0.45)

    To avoid that, UtilsX follows the `_TO_` convention, and declares
    that all such constants should be used as multipliers.

## Time

Constants like:

- `SECONDS_IN_MINUTE`
- `MINUTES_IN_DAY`
- `HOURS_IN_YEAR`

And tens more of the same nature, following the naming semantics `A_IN_B`.
Read them as _"How many units of `A` make up one unit of `B`"_.

While the [numeric](#numbers) constants help prevent typos,
and [physics](#physics) ones help achieve precision and consistency,
the **time** improves readability more than anything else.

Example:

``` py title="bad_practice.py"
# What does this conversion do: hours -> minutes or minutes -> seconds?
data["revenue"] /= 60
```

Do instead:

``` py title="good_practice.py"
from utilsx import MINUTES_IN_HOUR

data["revenue"] /= MINUTES_IN_HOUR
```

# 🧮 Math

Mathematical utilities that come handy in analytics pieces of your code.

## Collections

### [`check_values_add_up_to_one`][utilsx.math.check_values_add_up_to_one]

Useful in data validation to assure that values in a collection add up to 1 or 100.

Imagine a cooking recipe defined as proportions:

```py title="recipe.py" hl_lines="1 10"
from utilsx import check_values_add_up_to_one

recipe = {
    "water": 0.5,
    "sauce": 0.1,
    "potatoes": 0.25,
    "fish": 0.15,
}

check_values_add_up_to_one(recipe.values())
# True
```

By default, it returns `True` if values add up either to 1 or 100.
You can control this behavior using the `mode` argument.

### [`is_monotonically_growing`][utilsx.math.is_monotonically_growing]

Suppose you check memory usage of a long-running data processing job.
You expect fluctuations, but consistent exponential growth across intervals
likely signals a memory leak:

```py title="before.py" hl_lines="5-8"
# Memory usage sampled over time (in MB)
memory_readings = [200, 210, 225, 250, 290, 350]

# Manual leak detection logic
multiplier = 1.05  # Acceptable growth rate per interval
for i in range(len(memory_readings) - 1):
    if memory_readings[i + 1] <= memory_readings[i] * multiplier:
        break
else:
    raise RuntimeError("Potential memory leak: sustained growth detected")
```

Manual leak detection logic repeats across systems and lacks clarity.
The intent "memory grows too steadily" gets buried in low-level detail.

Use UtilsX to make it more concise:

```py title="after.py" hl_lines="1 7"
from utilsx import is_monotonically_growing

# Memory usage sampled over time (in MB)
memory_readings = [200, 210, 225, 250, 290, 350]

# Flag if memory grows steadily over time
if is_monotonically_growing(memory_readings, multiplier=1.05):
    raise RuntimeError("Potential memory leak: sustained growth detected")
```

`is_monotonically_growing` captures the intent behind the
check - guarding against unchecked growth - without relying on verbose loop logic.
The function works well in monitoring scripts,
system health checks, and automated alerting pipelines.

### [`normalize`][utilsx.math.normalize]

Helps you scale a sequence of numbers to add up to one, while keeping original relations.

```py title="portfolio.py" hl_lines="1 5"
from utilsx import normalize

holdings_usd = [300, 50, 120]

holdings_proportions = normalize(holdings_usd)
print(holdings_proportions)
# [0.6383, 0.1064, 0.2553]
```

## Division

### [`safe_divide`][utilsx.math.safe_divide]

Helps you avoid writing a `try` / `except ZeroDivisionError` clause when the divisor might equal zero.

```py title="return_on_equity.py" hl_lines="1 6"
from utilsx import safe_divide

profit = 12
equity = 0

roe = safe_divide(profit, equity)
print(f"Return on equity: {roe:.0%}")
# Return on equity: 0%
```

## Downscaling

### [`convert_number_to_units`][utilsx.math.convert_number_to_units]

Convert numbers to thousands / millions.

``` py title="downscaling.py" hl_lines="1 4"
from utilsx import convert_number_to_units

revenue_usd = 132890200
revenue_musd = convert_number_to_units(revenue_usd, "million")
print(revenue_musd)
# 132.8902
```

## Rounding

### [`ceil_to_multiple`][utilsx.math.ceil_to_multiple]

Like the built-in [`math.ceil`](https://docs.python.org/3/library/math.html#math.ceil),
but rounds up to a specified multiple.

Consider a shop with changes only in increments of $5:

``` py title="ceiling_to_multiple.py" hl_lines="1 4"
from utilsx import ceil_to_multiple

items_cost = 72
bill_amount = ceil_to_multiple(items_cost, 5)

print(bill_amount)
# 75
```

## Scalar operations

### [`double`][utilsx.math.double]

This function just doubles a number:

``` py title="doubling.py"
from utilsx import double

standard_price = 100
vip_price = double(standard_price)

print(vip_price)
# 200
```

This performs the same operation as `* 2`.

This helps to:

- Emphasize that the logic doubles the value,
  rather than multiplying by a number that currently equals 2 but might change.
- Help avoid typos and lint errors caused by a magic number.

### [`halve`][utilsx.math.halve]

The inverse of [`double`](#double).

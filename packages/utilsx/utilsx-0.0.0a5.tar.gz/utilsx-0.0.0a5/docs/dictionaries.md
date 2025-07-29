# 📋 Dictionaries

One-liners for operations you may commonly perform on dictionaries.

## Combination

### [`sum_dicts`][utilsx.dicts.sum_dicts]

Consider an example with two coffee shop locations,
each reporting sales as a dictionary, with the goal of
producing a dictionary of total sales:

``` py title="before.py" hl_lines="1 8-11"
from collections import defaultdict

# Sales from two locations
north_sales = {"coffee": 120, "cookie": 5, "juice": 40}
south_sales = {"coffee": 80, "cookie": 45, "banana": 10}

# Manual summation using defaultdict
combined_sales = defaultdict(int)
for location_sales in (north_sales, south_sales):
    for product, quantity in location_sales.items():
        combined_sales[product] += quantity

print(combined_sales)
# {"coffee": 200, "cookie": 50, "juice": 40, "banana": 10}
```

!!! question "Why avoid this approach?"

    Note that the dictionary summation logic takes more than half of the code: 5 lines out of 8.
    But nothing in it relates specifically to business logic - combining sales.

Use UtilsX to drastically simplify the preceding code:

``` py title="after.py" hl_lines="1 8"
from utilsx import sum_dicts

# Sales from two locations
north_sales = {"coffee": 120, "cookie": 5, "juice": 40}
south_sales = {"coffee": 80, "cookie": 45, "banana": 10}

# Summation using UtilsX function
combined_sales = sum_dicts(north_sales, south_sales)

print(combined_sales)
# {"coffee": 200, "cookie": 50, "juice": 40, "banana": 10}
```

## Filtering

### [`remove_items_with_zero_values`][utilsx.dicts.remove_items_with_zero_values]

Consider a case where a coffee shop tracks product sales, but some items haven’t sold at all.
The sales report includes all items, even those with zero sales - which clutters the output
and may cause confusion in downstream reporting.

``` py title="before.py" hl_lines="11"
# Sales including items with zero quantity
sales_report = {
    "coffee": 200,
    "cookie": 0,
    "juice": 40,
    "banana": 0,
    "sandwich": 25,
}

# Filtering using a dictionary comprehension
cleaned_report = {item: qty for item, qty in sales_report.items() if qty}

print(cleaned_report)
# {"coffee": 200, "juice": 40, "sandwich": 25}
```

!!! question "Why avoid this approach?"

    The filtering logic still mixes with business logic — it obscures the intent to simply "clean up the report."
    Repeating this pattern across different places increases maintenance cost.

Use UtilsX to cleanly filter the sales report:

``` py title="after.py" hl_lines="1 13"
from utilsx import remove_items_with_zero_values

# Sales including items with zero quantity
sales_report = {
    "coffee": 200,
    "cookie": 0,
    "juice": 40,
    "banana": 0,
    "sandwich": 25,
}

# Remove zero-value entries using UtilsX
cleaned_report = remove_items_with_zero_values(sales_report)

print(cleaned_report)
# {"coffee": 200, "juice": 40, "sandwich": 25}
```

## Modification

### [`multiply_dict_values`][utilsx.dicts.multiply_dict_values]

Consider a scenario where an inventory system stores product weights in kilograms,
but a downstream system - for example, a shipping provider - requires the same data in pounds.

``` py title="before.py" hl_lines="9-12"
# Product weights in kilograms
product_weights_kg = {
    "coffee_beans": 12.5,
    "cookies": 3.0,
    "juice_boxes": 8.75,
}

# Manual conversion to pounds
product_weights_lb = {
    weight_kg * 2.20462
    for item, weight_kg in product_weights_kg.items()
}

print(product_weights_lb)
# {"coffee_beans": 27.558, "cookies": 6.614, "juice_boxes": 19.290}
```

!!! question "Why avoid this approach?"

    The logic for applying a constant multiplier gets mixed in with the business need — unit conversion.
    It adds noise and reduces reuse in other places requiring the same transformation.

    Another issue with the code above is a hard-coded `2.20462` ratio.

Use UtilsX to cleanly express unit conversion:

``` py title="after.py" hl_lines="1 11"
from utilsx import KG_TO_LBS, multiply_dict_values

# Product weights in kilograms
product_weights_kg = {
    "coffee_beans": 12.5,
    "cookies": 3.0,
    "juice_boxes": 8.75,
}

# Convert to pounds
product_weights_lb = multiply_dict_values(product_weights_kg, KG_TO_LBS)

print(product_weights_lb)
# {"coffee_beans": 27.558, "cookies": 6.614, "juice_boxes": 19.290}
```

### [`rename_keys_in_nested_dict`][utilsx.dicts.rename_keys_in_nested_dict]

Consider a scenario where you’re processing a legacy configuration file
in a deeply nested dictionary format.
Teams authored this file over many years,
and some keys have outdated or inconsistent names.

You want to rename `"usr"` and `"pwd"` key names across all levels of nesting to
`"user"` and `"password"` respectively.

``` py title="config_example.py" hl_lines="3-4 12-13"
legacy_config = {
    "db_config": {
        "usr": "admin",
        "pwd": "secret",
        "host": "localhost",
        "port": 5432,
    },
    "log_settings": {
        "lvl": "INFO",
        "dir": "/var/log/app",
        "otel_credentials": {
            "usr": "otel_admin",
            "pwd": "otel_password",
        },
    },
}
```

Use UtilsX to rename those keys at all levels in one line:

``` py title="utilsx_workflow.py" hl_lines="1 5-11 16-17 25-26"
from utilsx import rename_keys_in_nested_dict

legacy_config = {...}

relevant_config = rename_keys_in_nested_dict(
    dictionary=legacy_config,
    renaming={
        "usr": "user",
        "pwd": "password",
    },
)

print(relevant_config)
# {
#     "db_config": {
#         "user": "admin",
#         "password": "secret",
#         "host": "localhost",
#         "port": 5432,
#     },
#     "log_settings": {
#         "lvl": "INFO",
#         "dir": "/var/log/app",
#         "otel_credentials": {
#             "user": "otel_admin",
#             "password": "otel_password",
#         },
#     },
# }
```

## Sorting

### [`sort_by_value`][utilsx.dicts.sort_by_value]

You can use Python's built-in `sorted` function to sort a dictionary by value,
but that requires specifying a lambda function.

Because this task occurs frequently, UtilsX offers a shorthand to simplify it:

``` py title="sort_by_value.py" hl_lines="1 11"
from utilsx import sort_by_value

product_revenue = {
    "coffee": 2400,
    "juice": 1200,
    "cookie": 800,
    "banana": 1600,
}

# Sort products by revenue, highest first
top_selling = sort_by_value(product_revenue, reverse=True)

print(top_selling)
# {"coffee": 2400, "banana": 1600, "juice": 1200, "cookie": 800}
```

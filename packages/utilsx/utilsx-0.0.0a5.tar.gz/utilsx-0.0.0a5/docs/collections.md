# 🗄️ Collections

One-liners for operations you may commonly perform on collections.

### [`check_equal_length`][utilsx.collections.check_equal_length]

Consider a scenario where you receive synchronized lists of product information -
such as names, prices, and stock levels - and need to verify that the data aligns
before further processing:

``` py title="manual.py" hl_lines="7"
# Raw product data
product_names = ["coffee", "cookie", "juice"]
product_prices = [3.5, 2.0]  # Missing price for "juice"
product_stock = [120, 85, 40]

# Manual length check
if not (len(product_names) == len(product_prices) == len(product_stock)):
    raise ValueError("Mismatched product data lengths")
```

Use UtilsX to perform that in a cleaner way:

``` py title="with_utilsx.py" hl_lines="1 9"
from utilsx import check_equal_length

# Raw product data
product_names = ["coffee", "cookie", "juice"]
product_prices = [3.5, 2.0]
product_stock = [120, 85, 40]

# Clean, readable validation
if not check_equal_length(product_names, product_prices, product_stock):
    raise ValueError("Mismatched product data lengths")
```

### [`get_duplicates`][utilsx.collections.get_duplicates]

Imagine importing product SKUs from multiple warehouse systems
and needing to identify duplicates before merging the inventory:

``` py title="manual.py" hl_lines="1 10-11"
from collections import Counter

# Combined list of product SKUs
skus = [
    "SKU123", "SKU456", "SKU789",
    "SKU123", "SKU999", "SKU456"
]

# Manual duplicate detection
sku_counts = Counter(skus)
duplicates = {sku for sku, count in sku_counts.items() if count > 1}

print(duplicates)
# {"SKU123", "SKU456"}
```

Use UtilsX to make that much cleaner:

``` py title="with_utilsx.py" hl_lines="1 10"
from utilsx import get_duplicates

# Combined list of product SKUs
skus = [
    "SKU123", "SKU456", "SKU789",
    "SKU123", "SKU999", "SKU456"
]

# Identify duplicate SKUs
duplicates = get_duplicates(skus)

print(duplicates)
# {"SKU123", "SKU456"}
```

### [`is_collection_of_equal_elements`][utilsx.collections.is_collection_of_equal_elements]

Suppose you check a batch of sensor readings to ensure stability -
you require all readings in a window to match before taking action:

``` py title="manual.py" hl_lines="5-6"
# Sensor readings over a time window
readings = [42, 42, 42, 42]

# Manual check for uniformity
first = readings[0]
if not all(r == first for r in readings):
    raise ValueError("Sensor values are unstable")
```

Use UtilsX to express that logic nicer:

``` py title="with_utilsx.py" hl_lines="1 6"
from utilsx import is_collection_of_equal_elements

# Sensor readings over a time window
readings = [42, 42, 42, 42]

if not is_collection_of_equal_elements(readings):
    raise ValueError("Sensor values are unstable")
```

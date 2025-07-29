# 🐻‍❄️ Pandas

Utilities for working with Pandas.

### [`count_na`][utilsx.pandas.count_na]

Pandas DataFrame lacks a built-in property for counting total missing values
across the entire dataframe, so this utility function provides that capability.

```py hl_lines="2 5"
import pandas as pd
from utilsx.pandas import count_na

df = pd.DataFrame(...)
if count_na(df):
    print("Dataframe has missing values!")
```

This technique helps during unit tests of data cleaning functions,
especially when confirming that the logic retains certain missing values.

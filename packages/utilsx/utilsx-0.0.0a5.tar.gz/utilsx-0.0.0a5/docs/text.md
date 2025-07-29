# 📝 Text

String utilities missing in the standard library, or complementing it nicely.

### [`add_suffix`][utilsx.text.add_suffix]

Imagine naming files for multiple versions of a report
with a consistent way to append version identifiers:

``` py title="manual.py" hl_lines="4-7"
report_name = "Q1_financials"
version = "v2"

if version:
    final_name = report_name + "_" + version
else:
    final_name = report_name

print(final_name)
# "Q1_financials_v2"
```

This logic appears simple, but repetition across the codebase leads to inconsistency,
unnecessary branching, and cluttered string operations.

Use UtilsX to streamline suffix construction:

``` py title="with_utilsx.py" hl_lines="1 6"
from utilsx import add_suffix

report_name = "Q1_financials"
version = "v2"

final_name = add_suffix(report_name, version)

print(final_name)
# "Q1_financials_v2"
```

You can also change the separator:

``` py
add_suffix("client", "archived", separator="-")
# "client-archived"
```

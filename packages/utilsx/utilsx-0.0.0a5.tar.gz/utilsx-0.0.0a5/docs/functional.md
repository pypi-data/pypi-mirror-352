# ➰ Functional

Utilities for functional programming.

### [`identity`][utilsx.functional.identity]

Takes a single object and returns it right away.

Other open source libraries
[provide it](https://toolz.readthedocs.io/en/latest/_modules/toolz/functoolz.html#identity),
but current implementation stands out thanks to proper typing via `TypeVar`.

It helps an IDE to automatically highlight errors like this:

```py title="highlighted_error.py" hl_lines="6-7"
from utilsx.functional import identity

number = identity(3)
text = identity("apple")

# IDE warns about this guaranteed TypeError
combo = number + text
```

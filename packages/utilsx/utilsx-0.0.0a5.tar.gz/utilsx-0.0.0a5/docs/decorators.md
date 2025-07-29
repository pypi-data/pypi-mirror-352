# 🎨 Decorators

Decorators to assist you in adjusting functions' behavior.

### [`narrow_return`][utilsx.decorators.narrow_return]

This decorator modifies a function which returns multiple elements
to only return one, at a specified index of the returned tuple.

Consider [`plot_series` function](https://www.sktime.net/en/latest/api_reference/auto_generated/sktime.utils.plotting.plot_series.html)
from the `sktime` library, which returns two elements:

1. A `matplotlib` figure: `plt.Figure`
1. An axis object: `plt.Axis`

```py title="original_workflow.py"
from sktime.utils.plotting import plot_series
from sktime.datasets import load_airline

y = load_airline()
fig, ax = plot_series(y)
```

Oftentimes you only care about the former.

You can adjust this function to only return a `fig`:

```py title="narrow_return.py" hl_lines="3 5 8"
from sktime.utils.plotting import plot_series
from sktime.datasets import load_airline
from utilsx import narrow_return

plot_series_to_figure = narrow_return(0)(plot_series)

y = load_airline()
fig = plot_series_to_figure(y)
```

This can help while working with orchestration frameworks
like [Kedro](`https://docs.kedro.org/en/stable/`), where unused elements in the returned tuple
clutter the directed acyclic graph.

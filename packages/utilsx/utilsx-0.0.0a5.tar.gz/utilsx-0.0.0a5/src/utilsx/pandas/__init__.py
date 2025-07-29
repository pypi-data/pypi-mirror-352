"""Utilities for enhancing your Pandas workflows."""

from utilsx.exceptions import hint_if_extra_uninstalled as _hint_if_extra_uninstalled

_hint_if_extra_uninstalled(
    required_modules=frozenset(("pandas",)),
    extra_name="pandas",
    package_name="utilsx",
)

# This import should be after the dependency group check logic.
from ._missing import *  # noqa: E402

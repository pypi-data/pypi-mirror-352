"""Utilities for raising exceptions."""

from collections.abc import Collection, Iterable
from difflib import get_close_matches
from importlib import import_module
from typing import NoReturn

__all__ = [
    "hint_if_extra_uninstalled",
    "prohibit_negative_values",
    "raise_key_error_with_suggestions",
]


def hint_if_extra_uninstalled(
    required_modules: Iterable[str],
    extra_name: str,
    package_name: str,
) -> None:
    """Check if an optional dependency group is installed, and hint if not, via ``ImportError``.

    Args:
        required_modules: Modules which need to be installed in venv for that dependency group.
        extra_name: Name of an optional dependency group.
        package_name: Name of the package which provides a given optional dependency group.

    Raises:
        ImportError: If any of the required modules are not installed.
    """
    for module in required_modules:
        try:
            import_module(module)
        except ImportError as e:
            raise ImportError(
                f"Optional dependency group '{extra_name}' is required for this feature.\n"
                f"Add '{package_name}[{extra_name}]' to your requirements list"
                " and install to virtual environment."
            ) from e


def prohibit_negative_values(
    values: Iterable[float],
    exception_class: type[Exception] = ValueError,
    exception_msg: str = "Negative values are prohibited",
) -> None:
    """Raise an exception if an iterable of numbers has negative values.

    Args:
        values: To check for any negative member.
        exception_class: Exception class to raise if any member is negative,
            defaults to ``ValueError``.
        exception_msg: A message to add to the raised exception.

    Returns:
        None.
    """
    if any(value < 0 for value in values):
        raise exception_class(exception_msg)


def raise_key_error_with_suggestions(
    attempted_key: str,
    existing_keys: Collection[str],
    object_name: str = "object",
    attribute_name: str = "key",
) -> NoReturn:
    """Raise a key error complemented with suggestions based on closest matches.

    Args:
        attempted_key: A key that was attempted to be found.
        existing_keys: Existing keys, among which an attempted key was not found.
        object_name: Archetype of an object that was searched by key.
        attribute_name: If this key represents an attribute with explicit name.

    Returns:
        Never returns anything.

    Raises:
        KeyError: Complemented with close matches, if any.

    Notes:
        Inspired by dataset name hint implemented in Kedro: https://github.com/kedro-org/kedro
    """
    error_msg = f"{object_name.capitalize()} with {attribute_name} {attempted_key} not found."
    close_matches = get_close_matches(attempted_key, existing_keys)
    if close_matches:
        suggestions = ", ".join(close_matches)
        error_msg += f" Did you mean one of these instead: {suggestions}?"
    raise KeyError(error_msg)

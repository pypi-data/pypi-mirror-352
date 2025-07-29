"""A collection of type variables."""

from typing import TypeVar

__all__ = [
    "NumberT",
    "T",
]

# Unbounded, unconstrained TypeVar to be used wherever input-output type match is needed.
T = TypeVar("T")

# TypeVar bounded to float, i.e., also includes int.
NumberT = TypeVar("NumberT", bound=float)

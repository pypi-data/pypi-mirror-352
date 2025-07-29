import re

import pytest

import utilsx.constants._physics as module


def test_each_constant_has_reverse() -> None:
    """Test that for each ``A_TO_B`` constant, ``B_TO_A`` is also defined."""
    constant_name_pattern = re.compile(r"^([A-Z]+)_TO_([A-Z]+)$")
    available_constant_names = frozenset(
        name for name in dir(module) if constant_name_pattern.match(name)
    )

    for name in available_constant_names:
        match = constant_name_pattern.match(name)
        if match:
            from_unit, to_unit = match.groups()
            reverse_name = f"{to_unit}_TO_{from_unit}"
            assert reverse_name in available_constant_names, (
                f"Missing reverse constant {reverse_name}, while {name} is defined"
            )
            assert getattr(module, name) == pytest.approx(1 / getattr(module, reverse_name)), (
                f"{reverse_name} should be the reciprocal of {name}"
            )
        else:
            raise RuntimeError(
                f"Constant {name} does not match expected pattern."
                " Review if the test body reflects naming convention"
            )

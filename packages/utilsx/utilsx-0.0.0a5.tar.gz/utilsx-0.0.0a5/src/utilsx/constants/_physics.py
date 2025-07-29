"""Physical conversions and ratios.

Naming convention is ``A_TO_B``, such that a value in units ``A``
**multiplied** by ``A_TO_B`` becomes the same amount in units ``B``.
"""

from typing import Final

GAL_TO_LITER: Final = 3.785411784
LITER_TO_GAL: Final = 1 / GAL_TO_LITER

GAL_TO_OZ: Final = 128
OZ_TO_GAL: Final = 1 / GAL_TO_OZ

LBS_TO_KG: Final = 0.45359237
KG_TO_LBS: Final = 1 / LBS_TO_KG

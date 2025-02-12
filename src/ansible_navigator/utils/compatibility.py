"""Conditional imports related to python versions."""

import sys

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    # https://mypy.readthedocs.io/en/stable/common_issues.html#variables-vs-type-aliases
    if sys.version_info >= (3, 10):
        from typing import TypeAlias
    else:
        from typing_extensions import TypeAlias

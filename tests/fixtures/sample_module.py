"""Sample Hamilton module used by the pytest-hamilton test suite.

This module defines a tiny DAG:

    x, y  ──►  add  ──►  add_doubled
          ──►  multiply
"""


def add(x: int, y: int) -> int:
    """Sum of two integers."""
    return x + y


def multiply(x: int, y: int) -> int:
    """Product of two integers."""
    return x * y


def add_doubled(add: int) -> int:
    """Double the sum — a downstream node that depends on *add*."""
    return add * 2

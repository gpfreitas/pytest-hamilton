"""Simple DAG to compute::

    x_plus_y = x + y
    final = x_plus_y**2
"""



def x_plus_y(x: int, y: int) -> int:
    return x + y


def final(x_plus_y: int) -> int:
    return x_plus_y**2

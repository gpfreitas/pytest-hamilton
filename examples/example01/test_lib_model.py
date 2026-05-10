

def test_x_plus_y(x_plus_y, x, y):
    assert x_plus_y - x == y


def test_final(final, x_plus_y):
    factor = final / x_plus_y
    assert factor == x_plus_y

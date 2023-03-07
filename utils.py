def clamp(value, min_level, max_level):
    """ Clamps a value in between a min and max inclusive. """

    assert min_level >= 0
    assert max_level >= 0
    assert min_level <= max_level

    if value < min_level:
        return min_level
    elif value > max_level:
        return max_level
    return value

def truncated_range(value, min_val, max_val):
    """
    Clamp value to be within the provided [min_val, max_val] range.
    Args:
        value: The value to check.
        min_val: Minimum allowable value.
        max_val: Maximum allowable value.
    Returns:
        The clamped value.
    """
    return max(min(value, max_val), min_val)

def truncated_discrete_set(value, allowed):
    """
    Force value into the closest allowed value from a discrete set.
    Args:
        value: The value to check.
        allowed: Iterable of allowed values.
    Returns:
        The closest allowed value.
    """
    if value not in allowed:
        return min(allowed, key=lambda x: abs(x - value))
    return value

def modular_range(value, min_val, max_val):
    """
    Wrap value into the range [min_val, max_val) (modulo operation).
    Args:
        value: The value to wrap.
        min_val: Minimum of range.
        max_val: Maximum of range (exclusive).
    Returns:
        Wrapped value within [min_val, max_val).
    """
    rng = max_val - min_val
    return (value - min_val) % rng + min_val

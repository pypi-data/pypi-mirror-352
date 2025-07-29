from ..types import NA


def safe_float(value):
    """
    Safe float conversion that returns NA for NA inputs.
    Catches TypeError (thrown by NA values) but allows ValueError to propagate normally.

    @param value: The value to convert to float.
    @return: The float value, or NA(float) if TypeError occurs.
    """
    try:
        return float(value)
    except TypeError:
        # NA values throw TypeError, convert these to NA
        return NA(float)


def safe_int(value):
    """
    Safe int conversion that returns NA for NA inputs.
    Catches TypeError (thrown by NA values) but allows ValueError to propagate normally.

    @param value: The value to convert to int.
    @return: The int value, or NA(int) if TypeError occurs.
    """
    try:
        return int(value)
    except TypeError:
        # NA values throw TypeError, convert these to NA
        return NA(int)

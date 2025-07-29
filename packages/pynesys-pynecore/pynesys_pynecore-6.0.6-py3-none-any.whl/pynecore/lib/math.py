from typing import TypeVar, cast
import builtins
import math

from ..types.na import NA
from ..types.series import Series

from ..utils.export import export

from . import syminfo

from ..core.series import SeriesImpl as _SeriesImpl
from ..core.random import PineRandom as _PineRandom
from ..core import safe_convert

TFI = TypeVar('TFI', float, int)

# Constants
e = math.e
pi = math.pi
phi = (1 + math.sqrt(5)) / 2
rphi = 1 / phi

export('e', 'pi', 'phi', 'rphi')

__persistent_function_vars__ = {}
__series_function_vars__ = {}


# noinspection PyShadowingBuiltins
@export
def abs(number: TFI | NA[TFI]) -> float | NA[float]:
    """
    Returns the absolute value of a number.

    :param number: A number.
    :return: The absolute value of the number.
    """
    if isinstance(number, NA):
        return NA(float)
    return builtins.abs(number)


@export
def acos(value: TFI | NA[TFI]) -> float | NA[float]:
    """
    Returns the arc cosine of a value.

    :param value: A value.
    :return: The arc cosine of the value.
    """
    if isinstance(value, NA):
        return NA(float)
    return math.acos(value)


@export
def asin(value: TFI | NA[TFI]) -> float | NA[float]:
    """
    Returns the arc sine of a value.

    :param value: A value.
    :return: The arc sine of the value.
    """
    if isinstance(value, NA):
        return NA(float)
    return math.asin(value)


@export
def atan(value: TFI | NA[TFI]) -> float | NA[float]:
    """
    Returns the arc tangent of a value.

    :param value: A value.
    :return: The arc tangent of the value.
    """
    if isinstance(value, NA):
        return NA(float)
    return math.atan(value)


@export
def avg(*numbers: TFI | NA[TFI]) -> float | NA[float]:
    """
    Returns the average of the numbers.

    :param numbers: Numbers.
    :return: The average of the numbers.
    """
    assert numbers, "At least one number is necessary!"

    if any(isinstance(n, NA) for n in numbers):
        return NA(float)

    return builtins.sum(cast(TFI, n) for n in numbers) / len(numbers)


@export
def ceil(number: TFI | NA[TFI]) -> float | NA[float]:
    """
    Returns the smallest integer greater than or equal to a number.

    :param number: A number.
    :return: The smallest integer greater than or equal to the number.
    """
    if isinstance(number, NA):
        return NA(float)
    return math.ceil(number)


@export
def cos(angle: TFI | NA[TFI]) -> float | NA[float]:
    """
    Returns the cosine of an angle.

    :param angle: An angle in radians.
    :return: The cosine of the angle.
    """
    if isinstance(angle, NA):
        return NA(float)
    return math.cos(angle)


@export
def exp(number: TFI | NA[TFI]) -> float | NA[float]:
    """
    Returns e raised to the power of a number.

    :param number: A number.
    :return: e raised to the power of the number.
    """
    if isinstance(number, NA):
        return NA(float)
    return math.exp(number)


@export
def floor(number: TFI | NA[TFI]) -> float | NA[float]:
    """
    Returns the largest integer less than or equal to a number.

    :param number: A number.
    :return: The largest integer less than or equal to the number.
    """
    if isinstance(number, NA):
        return NA(float)
    return int(number)


@export
def log(number: TFI | NA[TFI]) -> float | NA[float]:
    """
    Returns the natural logarithm of a number.

    :param number: A number.
    :return: The natural logarithm of the number.
    """
    if isinstance(number, NA):
        return NA(float)
    return math.log(number)


@export
def log10(number: TFI | NA[TFI]) -> float | NA[float]:
    """
    Returns the base-10 logarithm of a number.

    :param number: A number.
    :return: The base-10 logarithm of the number.
    """
    if isinstance(number, NA):
        return NA(float)
    return math.log10(number)


# noinspection PyShadowingBuiltins
@export
def max(*numbers: TFI | NA[TFI]) -> float | NA[float]:
    """
    Returns the largest number.

    :param numbers: Numbers.
    :return: The largest number.
    """
    assert numbers, "At least one number is necessary!"

    if any(isinstance(n, NA) for n in numbers):
        return NA(float)

    return builtins.max(cast(list[TFI], numbers))


# noinspection PyShadowingBuiltins
@export
def min(*numbers: TFI | NA[TFI]) -> float | NA[float]:
    """
    Returns the smallest number.

    :param numbers: Numbers.
    :return: The smallest number.
    """
    assert numbers, "At least one number is necessary!"

    if any(isinstance(n, NA) for n in numbers):
        return NA(float)

    return builtins.min(cast(list[TFI], numbers))


# noinspection PyShadowingBuiltins
@export
def pow(base: TFI | NA[TFI], exponent: TFI | NA[TFI]) -> float | NA[float]:
    """
    Returns a number raised to the power of another number.

    :param base: The base number.
    :param exponent: The exponent number.
    :return: The base number raised to the power of the exponent number.
    """
    if isinstance(base, NA) or isinstance(exponent, NA):
        return NA(float)

    return base ** exponent


__persistent_random_prng__: _PineRandom | None = None
__persistent_function_vars__['random'] = ['__persistent_random_prng__']


# noinspection PyShadowingBuiltins,PyShadowingNames
@export
def random(min: TFI | NA[TFI] = 0, max: TFI | NA[TFI] = 1, seed: int | NA[int] = NA(int)) -> float | NA[float]:
    """
    Returns a random number between two numbers.

    :param min: The minimum number.
    :param max: The maximum number.
    :param seed: The seed for the random number generator.
    :return: A random number between the minimum and maximum numbers.
    """
    global __persistent_random_prng__
    if __persistent_random_prng__ is None:
        __persistent_random_prng__ = _PineRandom(seed)
    res = __persistent_random_prng__.random(min, max)
    return res


# noinspection PyShadowingBuiltins
@export
def round(number: TFI | NA[TFI], precision: int | NA[int] = NA(int)) -> float | NA[float]:
    """
    Returns a number rounded to a specified number of decimal places.

    :param number: A number.
    :param precision: The number of decimal places to round to.
    :return: The rounded number.
    """
    if isinstance(number, NA):
        return NA(float)
    print(f"number: {number}, precision: {precision}")
    if isinstance(precision, NA):
        return builtins.round(number)
    return builtins.round(number, precision)


@export
def round_to_mintick(number: TFI | NA[TFI]) -> float | NA[float]:
    """
    Returns value rounded to symbol's mintick with ties rounding up.
    """
    return int(number / syminfo.mintick + 0.5) * syminfo.mintick


@export
def sign(number: TFI | NA[TFI]) -> float | NA[float]:
    """
    Returns the sign of a number.

    :param number: A number.
    :return: The sign of the number.
    """
    if isinstance(number, NA):
        return NA(float)
    if number == 0.0:
        return 0.0
    if number > 0.0:
        return 1.0
    return -1.0


@export
def sin(angle: float | int | NA) -> float | NA[float]:
    """
    Returns the sine of an angle.

    :param angle: An angle in radians.
    :return: The sine of the angle.
    """
    if isinstance(angle, NA):
        return NA(float)
    return math.sin(angle)


@export
def sqrt(number: float | int | NA) -> float | NA[float]:
    """
    Returns the square root of a number.

    :param number: A number.
    :return: The square root of the number.
    """
    if isinstance(number, NA):
        return NA(float)
    try:
        return math.sqrt(number)
    except ValueError:
        return NA(float)


__series_summ_source__: _SeriesImpl[float | NA[float]] = _SeriesImpl()
__persistent_summ_summ__: float = 0.0
__persistent_summ_count__: int = 0
__persistent_function_vars__['sum'] = ['__persistent_summ_summ__', '__persistent_summ_count__']
__series_function_vars__['sum'] = ['__series_summ_source__']


# noinspection PyShadowingBuiltins
@export
def sum(source: Series[TFI | NA[TFI]], length: int) -> float | NA[float] | Series[TFI | NA[TFI]]:
    """
    Returns the sum of a series over a specified length.

    :param source: Source series
    :param length: Length of the sum
    :return: The sliding sum of the series
    """
    global __series_summ_source__, __persistent_summ_summ__, __persistent_summ_count__

    if length == 1:  # Shortcut
        return source
    assert length > 0, "Invalid length, length must be greater than 0!"

    isna = isinstance(source, NA)
    if not isna:
        __series_summ_source__.add(source)

    if __persistent_summ_count__ < length - 1:
        if not isna:
            __persistent_summ_count__ += 1
            __persistent_summ_summ__ += source
        return NA(float)
    elif __persistent_summ_count__ == length - 1:
        if isna:
            return NA(float)
        __persistent_summ_count__ += 1
    else:
        if isna:
            return __persistent_summ_summ__
        __persistent_summ_summ__ -= safe_convert.safe_float(__series_summ_source__[length])

    __persistent_summ_summ__ += source

    return __persistent_summ_summ__


@export
def tan(angle: TFI | NA[TFI]) -> float | NA[float]:
    """
    Returns the tangent of an angle.

    :param angle: An angle in radians.
    :return: The tangent of the angle.
    """
    if isinstance(angle, NA):
        return NA(float)
    return math.tan(angle)


@export
def todegrees(angle: TFI | NA[TFI]) -> float | NA[float]:
    """
    Converts an angle from radians to degrees.

    :param angle: An angle in radians.
    :return: The angle in degrees.
    """
    if isinstance(angle, NA):
        return NA(float)
    return math.degrees(angle)


@export
def toradians(angle: TFI | NA[TFI]) -> float | NA[float]:
    """
    Converts an angle from degrees to radians.

    :param angle: An angle in degrees.
    :return: The angle in radians.
    """
    if isinstance(angle, NA):
        return NA(float)
    return math.radians(angle)

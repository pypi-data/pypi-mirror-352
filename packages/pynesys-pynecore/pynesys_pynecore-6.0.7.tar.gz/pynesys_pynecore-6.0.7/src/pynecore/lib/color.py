from ..types.color import Color

#
# Constants
#

aqua = Color('#00BCD4')
black = Color('#363A45')
blue = Color('#2962ff')
fuchsia = Color('#E040FB')
gray = Color('#787B86')
green = Color('#4CAF50')
lime = Color('#00E676')
maroon = Color('#880E4F')
navy = Color('#311B92')
olive = Color('#808000')
orange = Color('#FF9800')
purple = Color('#9C27B0')
red = Color('#F23645')
silver = Color('#B2B5BE')
teal = Color('#089981')
white = Color('#FFFFFF')
yellow = Color('#FDD835')


def r(color: Color) -> int:
    """
    Return the red component of a color

    :param color: Color
    :return: The red component of the color
    """
    return color.r


def g(color: Color) -> int:
    """
    Return the green component of a color

    :param color: Color
    :return: The green component of the color
    """
    return color.g


def b(color: Color) -> int:
    """
    Return the blue component of a color

    :param color: Color
    :return: The blue component of the color
    """
    return color.b


def t(color: Color) -> int:
    """
    Return the transparency of a color

    :param color: Color
    :return: The transparency of the color, 0-100 (0: not transparent, 100: invisible)
    """
    return color.a


# noinspection PyShadowingNames
def new(color: Color | str, transp: float = 0) -> Color:
    """
    Return a new color with the same RGB values and a different transparency

    :param color: A color object or a string in "#RRGGBB" or "#RRGGBBAA" format
    :param transp: Transparency percentage (0-100, 0: not transparent, 100: invisible)
    """
    if isinstance(color, str):
        color = Color(color)
    color.t = transp
    return color


# noinspection PyShadowingNames
def rgb(r: int, g: int, b: int, transp: float = 0) -> Color:
    """
    Return a new color with the given RGB values and transparency

    :param r: Red value
    :param g: Green value
    :param b: Blue value
    :param transp: Transparency percentage (0-100, 0: not transparent, 100: invisible)
    """
    return Color.rgb(r, g, b, transp)

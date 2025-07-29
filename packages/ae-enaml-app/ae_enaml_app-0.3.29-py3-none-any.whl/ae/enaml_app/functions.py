""" enaml application helper functions. """
from typing import Tuple
from enaml.colorext import Color    # type: ignore # pylint:disable=no-name-in-module


def ae_rgba(color: Color) -> Tuple[float, float, float, float]:
    """ convert enaml Color instance into ae color format.

    :param color:   enaml Color instance.
    :return:        rgba tuple with 4 float values (0.0 ... 1.0).
    """
    return color.red / 255.0, color.green / 255.0, color.blue / 255.0, color.alpha / 255.0


def enaml_rgba(red: float, green: float, blue: float, alpha: float) -> Color:
    """ convert ae color rgba floats into enaml compatible rgba integers.

    :param red:     red color value (0.0 ... 1.0).
    :param green:   green color value (0.0 ... 1.0).
    :param blue:    blue color value (0.0 ... 1.0).
    :param alpha:   alpha/opacity value (0.0 ... 1.0).
    :return:        rgba enaml Color instance (0 ... 255).
    """
    return Color(int(red * 255), int(green * 255), int(blue * 255), int(alpha * 255))


def style_rgba(red: float, green: float, blue: float, alpha: float) -> str:
    """ convert ae color rgba floats into Qt style compatible rgba color string.

    :param red:     red color value (0.0 ... 1.0).
    :param green:   green color value (0.0 ... 1.0).
    :param blue:    blue color value (0.0 ... 1.0).
    :param alpha:   alpha/opacity value (0.0 ... 1.0).
    :return:        rgba enaml Color instance (0 ... 255).
    """
    return f"rgba({int(red * 255), int(green * 255)}, {int(blue * 255)}, {int(alpha * 100)}%)"

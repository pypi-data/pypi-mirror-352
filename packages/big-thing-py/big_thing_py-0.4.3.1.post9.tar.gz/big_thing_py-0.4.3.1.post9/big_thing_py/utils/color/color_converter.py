import webcolors
from rgbxy import Converter
import colorsys
from typing import Tuple, Union


class ColorConverter:
    def __init__(self) -> None:
        pass

    @staticmethod
    def name_to_rgb(color_name: str) -> webcolors.IntegerRGB:
        try:
            integer_rgb = webcolors.name_to_rgb(color_name)
            return integer_rgb
        except ValueError:
            return None

    @staticmethod
    def rgb_to_name(rgb: Tuple[int, int, int]) -> Union[str, None]:
        try:
            color_name = webcolors.rgb_to_name(rgb)
            return color_name
        except ValueError:
            return None

    @staticmethod
    def hex_to_rgb(hex_value: str) -> Tuple[int, int, int]:
        try:
            rgb = webcolors.hex_to_rgb(hex_value)
            return rgb
        except ValueError:
            return None

    @staticmethod
    def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
        try:
            hex_value = webcolors.rgb_to_hex(rgb)
            return hex_value
        except ValueError:
            return None

    @staticmethod
    def xy_to_rgb(x, y, bri=1):
        r, g, b = Converter().xy_to_rgb(x=x, y=y, bri=bri)
        return r, g, b

    @staticmethod
    def rgb_to_xy(red, green, blue):
        x, y = Converter().rgb_to_xy(red=red, green=green, blue=blue)
        return x, y

    @staticmethod
    def hsv_to_rgb(h, s, v):
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return r, g, b

    @staticmethod
    def rgb_to_hsv(r, g, b):
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        return h, s, v

    @staticmethod
    def rgb_to_str(color0: Union[int, float], color1: Union[int, float], color2: Union[int, float]) -> str:
        return f'{color0:0.4f}|{color1:0.4f}|{color2:0.4f}'

    @staticmethod
    def str_to_rgb(color_str: str) -> Tuple[int, int, int]:
        return tuple(map(float, color_str.split('|')))


if __name__ == '__main__':
    print(ColorConverter.name_to_rgb('red'))
    print(ColorConverter.rgb_to_name((255, 0, 0)))
    print(ColorConverter.hex_to_rgb('#FF0000'))
    print(ColorConverter.rgb_to_hex((255, 0, 0)))
    print(ColorConverter.xy_to_rgb(0.5, 0.5))
    print(ColorConverter.rgb_to_xy(255, 0, 0))
    print(ColorConverter.hsv_to_rgb(0.0, 1.0, 1.0))
    print(ColorConverter.rgb_to_hsv(255, 0, 0))
    print(ColorConverter.rgb_to_str(0.0, 0.0, 0.0))
    print(ColorConverter.str_to_rgb('0.0|0.0|0.0'))

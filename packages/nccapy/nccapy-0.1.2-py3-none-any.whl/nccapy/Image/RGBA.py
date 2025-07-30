import colorsys
from typing import Tuple


class RGBA:
    # fmt: off
    red_mask =   0x000000FF
    green_mask = 0x0000FF00
    blue_mask =  0x00FF0000
    alpha_mask = 0xFF000000
    # fmt: on

    def __init__(self, r: int = 0, g: int = 0, b: int = 0, a: int = 255):
        r = r & 0xFF
        g = g & 0xFF
        b = b & 0xFF
        a = a & 0xFF
        self.pixel = (a << 24) + (b << 16) + (g << 8) + r

    def get_rgba(self) -> Tuple[int, int, int, int]:
        alpha = (self.pixel & self.alpha_mask) >> 24
        blue = (self.pixel & self.blue_mask) >> 16
        green = (self.pixel & self.green_mask) >> 8
        red = self.pixel & self.red_mask
        return red, green, blue, alpha

    def alpha(self) -> int:
        return (self.pixel & self.alpha_mask) >> 24

    def red(self) -> int:
        return self.pixel & self.red_mask

    def green(self) -> int:
        return (self.pixel & self.green_mask) >> 8

    def blue(self) -> int:
        return (self.pixel & self.blue_mask) >> 16

    def set(self, r: int, g: int, b: int, a: int = 255):
        self.pixel = (a << 24) + (b << 16) + (g << 8) + r

    def as_hsv(self) -> Tuple[int, int, int]:
        # convert r,g,b to floats for rgb_to_hsv
        h, s, v = colorsys.rgb_to_hsv(
            self.red() / 255.0, self.green() / 255.0, self.blue() / 255.0
        )
        # We have H as an angle, s an v as percentages
        return round(360 * h), round(s * 100), round(v * 100)

    @classmethod
    def from_hex(cls, pixel: str) -> "RGBA":
        try:
            red = int(pixel[0:2], 16)
            green = int(pixel[2:4], 16)
            blue = int(pixel[4:6], 16)
            alpha = int(pixel[6:8], 16)
            return cls(red, green, blue, alpha)
        except ValueError:
            raise ValueError("Invalid hex string")

    @classmethod
    def from_pixel(cls, pixel: int) -> "RGBA":
        rgba = cls()
        rgba.pixel = pixel
        return rgba

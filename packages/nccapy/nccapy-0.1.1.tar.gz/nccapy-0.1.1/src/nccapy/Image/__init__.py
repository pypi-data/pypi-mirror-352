"""
The Image module contains classes for working with 2D images.

The image class stored the Image data as an array of RGBA values which
pack the data into a single 32-bit integer which is use quite a lot in computer graphics

"""

from .Canvas import Canvas
from .Image import Image
from .RGBA import RGBA

__all__ = ["Image", "RGBA", "Canvas"]

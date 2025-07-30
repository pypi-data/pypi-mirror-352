"""
nccapy module

This module is used in the NCCA Python programming courses for more details see here
https://nccastaff.bournemouth.ac.uk/jmacey/

Available submodules
--------------------
Math
    This contains simple Vec3,Vec4,Mat3,Mat4 and Transform classes for 3D math.
Geo
    Provides a Simple Mesh type class for creating and loading Obj files
Image
    Provides classes for simple images and RGBA color values allowing the setting and getting of pixels

Classes
-------
Vec2
    A class for 2D vectors.
Vec3
    A class for 3D vectors.
Vec4
    A class for 4D vectors.
Mat3
    A class for 3x3 matrices.
Mat4
    A class for 4x4 matrices.
Transform
    A class for transformations.
Obj
    A class for 3D objects.
Timer
    A class for timing operations.
Image
    A class for images.
RGBA
    A class for RGBA color values.
"""

from nccapy.Geo import Obj
from nccapy.Image import RGBA, Image # note canvas not impoorted as it inits pygame which is not needed for the nccapy module
from nccapy.Math import Mat3, Mat4, Transform, Util, Vec3, Vec4,Vec2
from nccapy.Math.Util import clamp, lerp, look_at, perspective

__all__ = [
    "Vec2",
    "Vec3",
    "Vec4",
    "Mat3",
    "Mat4",
    "Transform",
    "Obj",
    "Image",
    "RGBA",
    "Util",
    "perspective",
    "look_at",
    "clamp",
    "lerp",
]

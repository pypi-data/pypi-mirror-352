"""
The Math module contains classes used in 3D graphics, they are simple
examples of generating Vectors and Matrices and performing operations on them.
This is not a complete math library and is not optimized for performance, and should be used
for educational purposes only, I suggest using a library like numpy for any real work or the
relevant DCC math libraries like Maya's OpenMaya or Blender's mathutils.

Classes:
    Mat3: A 3x3 matrix class.
    Mat4: A 4x4 matrix class.
    Transform: A class for representing 3D transformations as a 4x4 matrix.
    Vec3: A 3D vector class.
    Vec4: A 4D vector class.
    Util: A set of utility functions for working with vectors and matrices.

    see here for more information:
    https://nccastaff.bournemouth.ac.uk/jmacey/post/PythonClasses/pyclasses/
    https://nccastaff.bournemouth.ac.uk/jmacey/post/AutoTest/autotest/

"""

from .Mat3 import Mat3
from .Mat4 import Mat4
from .Transform import Transform
from .Util import clamp, look_at, perspective
from .Vec2 import Vec2
from .Vec3 import Vec3
from .Vec4 import Vec4

__all__ = [
    "Mat3",
    "Mat4",
    "Transform",
    "Vec2",
    "Vec3",
    "Vec4",
    "Util",
    "clamp",
    "look_at",
    "perspective",
]

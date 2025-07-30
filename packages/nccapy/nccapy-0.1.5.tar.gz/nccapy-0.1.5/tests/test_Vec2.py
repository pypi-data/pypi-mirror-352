import pytest
import copy
from nccapy.Math.Mat2 import Mat2
from nccapy.Math.Vec2 import Vec2


def test_properties():
    v = Vec2()
    v.x = 2.0
    v.y = 3.0
    assert v.x == pytest.approx(2.0)
    assert v.y == pytest.approx(3.0)
    with pytest.raises(ValueError):
        v.x = "fail"
    with pytest.raises(ValueError):
        v.y = "fail"


def test_ctor():
    v = Vec2()
    assert v.x == pytest.approx(0.0)
    assert v.y == pytest.approx(0.0)


def test_userCtor():
    v = Vec2(2.0, 3.0)
    assert v.x == pytest.approx(2.0)
    assert v.y == pytest.approx(3.0)


def test_ctor_single_value():
    v = Vec2(x=2.0)
    assert v.x == pytest.approx(2.0)
    assert v.y == pytest.approx(0.0)

    v = Vec2(y=2.0)
    assert v.x == pytest.approx(0.0)
    assert v.y == pytest.approx(2.0)



def test_add():
    a = Vec2(1, 2 )
    b = Vec2(4, 5)
    c = a + b
    assert c.x == pytest.approx(5)
    assert c.y == pytest.approx(7)

    # negative test
    a = Vec2(1, 2)
    b = Vec2(-4, -5)
    c = a + b
    assert c.x == pytest.approx(-3)
    assert c.y == pytest.approx(-3)


def test_plus_equals():
    a = Vec2(1, 2)
    b = Vec2(4, 5)
    a += b
    assert a.x == pytest.approx(5)
    assert a.y == pytest.approx(7)


def test_sub():
    a = Vec2(1, 2)
    b = Vec2(4, 5)
    c = a - b
    assert c.x == pytest.approx(-3)
    assert c.y == pytest.approx(-3)


def test_sub_equals():
    a = Vec2(1, 2)
    b = Vec2(4, 5)
    a -= b
    assert a.x == pytest.approx(-3)
    assert a.y == pytest.approx(-3)


def test_set():
    a = Vec2()
    a.set(2.5, 0.1)
    assert a.x == pytest.approx(2.5)
    assert a.y == pytest.approx(0.1)


def test_error_set():
    with pytest.raises(ValueError):
        a = Vec2()
        a.set(2, "hello")


def test_dot():
    a = Vec2(1.0, 2.0)
    b = Vec2(4.0, 5.0)
    assert a.dot(b) == pytest.approx(14.0, rel=1e-2)


def test_length():
    a = Vec2(22, 2.5)
    assert a.length() == pytest.approx(22.198, rel=1e-2)

def test_length_squared():
    a = Vec2(22, 32)
    assert a.length_squared() == pytest.approx(1508, rel=1e-2)


def test_normalize():
    a = Vec2(22.3, 0.5)
    a.normalize()
    assert a.x == pytest.approx(0.9996,rel=1e-2)
    assert a.y == pytest.approx(0.0224,rel=1e-2)
    with pytest.raises(ZeroDivisionError):
        a = Vec2(0, 0)
        a.normalize()


def test_equal():
    a = Vec2(0.1, 0.2)
    b = Vec2(0.1, 0.2)
    assert a == b
    assert a.__eq__(1) == NotImplemented


def test_not_equal():
    a = Vec2(0.3, 0.4)
    b = Vec2(0.1, 0.2)
    assert a != b
    a = Vec2(0.3, 0.4)
    b = Vec2(0.3, 0.2)
    assert a != b
    a = Vec2(0.3, 0.2)
    b = Vec2(0.3, 0.4)

    assert a.__neq__(1) == NotImplemented


def test_inner():
    a = Vec2(1.0, 2.0)
    b = Vec2(3.0, 4.0)
    inner = a.inner(b)
    assert inner == pytest.approx(11.0)


def test_negate():
    a = Vec2(0.1, 0.5)
    a = -a
    assert a.x == pytest.approx(-0.1)
    assert a.y == pytest.approx(-0.5)


def test_reflect():
    N = Vec2(0, 1)
    a = Vec2(2, 2)
    a.normalize()
    ref = a.reflect(N)
    assert ref.x == pytest.approx(0.707, rel=1e-2)
    assert ref.y == pytest.approx(-0.707, rel=1e-2)


def test_clamp():
    a = Vec2(0.1, 5.0)
    a.clamp(0.5, 1.8)
    assert a.x == pytest.approx(0.5)
    assert a.y == pytest.approx(1.8)




def test_null():
    a = Vec2(2, 3)
    a.null()
    assert a.x == pytest.approx(0.0)
    assert a.y == pytest.approx(0.0)


def test_cross():
    a = Vec2(2.0, 3.0)
    b = Vec2(5.0, 3.2)
    c = a.cross(b)
    assert c == pytest.approx(-8.6, rel=1e-2)  # 2*3.2 - 3*5

def test_mul_scalar():
    a = Vec2(1.0, 1.5)
    a = a * 2
    assert a.x == pytest.approx(2.0)
    assert a.y == pytest.approx(3.0)

    a = Vec2(1.5, 4.2)
    a = 2 * a
    assert a.x == pytest.approx(3.0)
    assert a.y == pytest.approx(8.4)

    with pytest.raises(ValueError):
        a = a * "hello"


def test_getAttr():
    a = Vec2(1, 2)
    assert getattr(a, "x") == pytest.approx(1.0)
    assert getattr(a, "y") == pytest.approx(2.0)

    # check to see if we can get non attr
    with pytest.raises(AttributeError):
        getattr(a, "b")
    # check to see that adding an attrib fails
    with pytest.raises(AttributeError):
        setattr(a, "b", 20.0)


# def test_matmul():
#     a = Vec2(1, 2, 3)
#     b = Mat3.rotate_x(45.0)
#     c = a @ b
#     assert c.x == pytest.approx(1.0)
#     assert c.y == pytest.approx(-0.707107, rel=1e-2)
#     assert c.z == pytest.approx(3.535534, rel=1e-2)


def test_string():
    a = Vec2(1, 2)
    assert str(a) == "[1,2]"
    assert repr(a) == "Vec2 [1,2]"


def test_iterable():
    a = Vec2(1, 2)
    b = [x for x in a]
    assert b == [1, 2]
    assert a[0] == 1
    assert a[1] == 2
    with pytest.raises(IndexError):
        a[2]

    v = []
    v.extend(a)
    assert v == [1, 2]


def test_copy():
    a = Vec2(1, 2)
    b = copy.copy(a)
    assert a == b
    b.x = 10
    assert a != b
    assert a.x == 1
    assert b.x == 10

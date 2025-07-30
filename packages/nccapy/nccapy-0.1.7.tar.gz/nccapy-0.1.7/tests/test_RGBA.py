import pytest

from nccapy.Image import RGBA


def test_ctor():
    pixel = RGBA()
    r, g, b, a = pixel.get_rgba()
    assert r == 0
    assert g == 0
    assert b == 0
    assert a == 255


def test_ctor_user():
    pixel = RGBA(123, 255, 0, 255)
    r, g, b, a = pixel.get_rgba()

    assert r == 123
    assert g == 255
    assert b == 0
    assert a == 255


def test_colour_access():
    pixel = RGBA(128, 255, 56, 25)
    assert pixel.red() == 128
    assert pixel.green() == 255
    assert pixel.blue() == 56
    assert pixel.alpha() == 25


def test_from_hex():
    pixel = RGBA.from_hex("FF2F3F00")
    assert pixel.red() == 255
    assert pixel.green() == 47
    assert pixel.blue() == 63
    assert pixel.alpha() == 0

    with pytest.raises(ValueError):
        pixel = RGBA.from_hex("nonsense")


def test_set():
    pixel = RGBA()
    pixel.set(255, 0, 0, 255)
    assert pixel.red() == 255
    assert pixel.green() == 0
    assert pixel.blue() == 0
    assert pixel.alpha() == 255


def test_to_hsv():
    test_values = [
        [(255, 0, 23), (355, 100, 100)],
        [(156, 146, 147), (354, 6, 61)],
        [(81, 118, 158), (211, 49, 62)],
    ]
    pixel = RGBA()
    for value in test_values:
        print(value)
        pixel.set(value[0][0], value[0][1], value[0][2])
        h, s, v = pixel.as_hsv()
        assert h == value[1][0]
        assert s == value[1][1]
        assert v == value[1][2]

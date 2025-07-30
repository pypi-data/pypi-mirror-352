import pytest

from nccapy.Math.Util import clamp, lerp, look_at, perspective
from nccapy.Math.Vec3 import Vec3


def test_clamp():
    assert clamp(2, 10, 20) == 10  # test  int up
    assert clamp(200, 10, 20) == 20  # test int down
    assert clamp(0.1, 0.01, 1.0) == 0.1
    assert clamp(2.1, 0.01, 1.2) == 1.2


def test_lerp():
    assert lerp(0, 1, 0.5) == 0.5
    assert lerp(0, 1, 0.1) == 0.1
    assert lerp(0, 1, 0.9) == 0.9


def test_clamp_error():
    with pytest.raises(ValueError):
        clamp(1, 100, 0.1)


def test_look_at():
    eye = Vec3(2, 2, 2)
    look = Vec3(0, 0, 0)
    up = Vec3(0, 1, 0)
    view = look_at(eye, look, up)
    # result from Julia function and same as GLM as well
    # fmt: off
    result=[0.7071067811865475, -0.4082482904638631, 0.5773502691896258 ,0.0, 0.0, 0.8164965809277261, 0.5773502691896258, 0.0, -0.7071067811865475, -0.4082482904638631, 0.5773502691896258 ,0.0, -0.0, -0.0, -3.4641016151377553, 1.0]
    # fmt: on
    assert view.get_matrix() == pytest.approx(result)


def test_perspective():
    project = perspective(45.0, 1.0, 0.1, 100)
    # fmt: off
    result=[2.4142135623730954, 0.0, 0.0, 0.0, 0.0 ,2.4142135623730954, 0.0 ,0.0,0.0 ,0.0, -1.002002002002002, -1.0, 0.0, 0.0, -0.20020020020020018, 0.0]
    # fmt: on
    assert project.get_matrix() == pytest.approx(result)

from point_algs import sign, brezenhem_float, vu
from class_point import Point
import pytest


@pytest.fixture
def null_point():
    return Point()


def segment(x1, y1, x2, y2):
    return Point(x1, y1), Point(x2, y2)


def test_sign_neg():
    assert sign(-6) == -1


def test_sign_pos():
    assert sign(6) == 1


def test_sign_null():
    assert sign(0) == 0


def test_brezenhem_float():
    ans = [[0.0, 0.0], [1.0, 0.0], [2.0, 0.0],
           [3.0, 0.0], [4.0, 0.0], [5.0, 0.0]]
    p1, p2 = segment(0, 0, 5, 0)
    res = brezenhem_float(p1, p2)
    for i in range(len(ans)):
        assert res[i].x == ans[i][0]
        assert res[i].y == ans[i][1]


def test_vu_point(null_point):
    ans = vu(null_point, null_point)
    for _ in ans:
        assert _[0].x == 0.0
        assert _[0].y == 0.0
        assert _[1] == 255

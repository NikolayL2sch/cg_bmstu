from typing import Tuple

import pytest
from class_point import Point
from point_funcs import add_symmetr_points
from brezenhem_algs import brezenhem_ellipse, sign, brezenhem_line


@pytest.fixture
def null_point():
    return Point()


def segment(x1: int, y1: int, x2: int, y2: int) -> Tuple[Point, Point]:
    return Point(x1, y1), Point(x2, y2)


def test_add_symmetr_points_null(null_point):
    result = add_symmetr_points(null_point, null_point)
    for point in result:
        assert point.x == 0 and point.y == 0


def test_add_symmetr_points_equal():
    result = add_symmetr_points(Point(5, 10), Point(5, 10))
    for point in result:
        assert point.x == 5 and point.y == 10


def test_ellipse_brezenhem(null_point):
    points = brezenhem_ellipse(null_point, 2, 5)
    result = [Point(0.0, 5.0), Point(0.0, 5.0), Point(0.0, -5.0), Point(0.0, -5.0),
              Point(-1.0, 4.0), Point(1.0, 4.0), Point(1.0, -
                                                       4.0), Point(-1.0, -4.0),
              Point(-1.0, 3.0), Point(1.0,
                                      3.0), Point(1.0, -3.0), Point(-1.0, -3.0),
              Point(-1.0, 2.0), Point(1.0,
                                      2.0), Point(1.0, -2.0), Point(-1.0, -2.0),
              Point(-1.0, 1.0), Point(1.0,
                                      1.0), Point(1.0, -1.0), Point(-1.0, -1.0),
              Point(-2.0, 0.0), Point(2.0, 0.0), Point(2.0, 0.0), Point(-2.0, 0.0)]
    for i in range(len(points)):
        assert int(points[i].x) == int(result[i].x) and int(
            points[i].y) == int(result[i].y)


def test_sign_neg():
    assert sign(-6) == -1


def test_sign_pos():
    assert sign(6) == 1


def test_sign_null():
    assert sign(0) == 0


def test_draw_line():
    ans = [[0.0, 0.0], [1.0, 0.0], [2.0, 0.0],
           [3.0, 0.0], [4.0, 0.0], [5.0, 0.0]]
    p1, p2 = segment(0, 0, 5, 0)
    res = brezenhem_line(p1, p2)
    for i in range(len(ans)):
        assert res[i].x == ans[i][0]
        assert res[i].y == ans[i][1]

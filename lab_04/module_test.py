from point_funcs import add_symmetr_points
from class_point import Point
from ellipse_algs import ellipse_brezenhem
import pytest


@pytest.fixture
def null_point():
    return Point()


def test_add_symmetr_points_null(null_point):
    result = add_symmetr_points(null_point, null_point)
    for point in result:
        assert point.x == 0 and point.y == 0


def test_add_symmetr_points_equal():
    result = add_symmetr_points(Point(5, 10), Point(5, 10))
    for point in result:
        assert point.x == 5 and point.y == 10


def test_ellipse_brezenhem(null_point):
    points = ellipse_brezenhem(null_point, 2, 5)
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

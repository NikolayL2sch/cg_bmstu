from PyQt5.QtGui import QVector2D

from class_point import Point
from cut_algs import get_segment_vector, get_vector_mul, check_convexity_polygon
import pytest


@pytest.fixture
def null_point():
    return Point()


def test_null_point_equality(null_point):
    assert null_point == Point(0, 0)


def test_get_segment_vector(null_point):
    vector = get_segment_vector(Point(0, 0), Point(2, 4))
    assert vector.x() == 2 and vector.y() == 4


def test_vector_mul():
    v1 = QVector2D(1, 2)
    v2 = QVector2D(3, 4)
    assert get_vector_mul(v1, v2) == -2


def test_vector_mul_null():
    v1 = QVector2D(0, 0)
    v2 = QVector2D(0, 0)
    assert get_vector_mul(v1, v2) == 0


def test_check_convexity_polygon_false():
    figure_points = [Point(-171, 225), Point(-235, -70),
                     Point(-59, 31), Point(103, 12)]
    assert not check_convexity_polygon(figure_points)


def test_check_convexity_polygon_true():
    figure_points = [Point(-133, 238), Point(-225, -63), Point(158, -40)]
    assert check_convexity_polygon(figure_points)

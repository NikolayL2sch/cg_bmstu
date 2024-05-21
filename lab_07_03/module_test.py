from class_point import Point
from point_funcs import get_code
import pytest


@pytest.fixture
def null_point():
    return Point()


def test_null_point_equality(null_point):
    assert null_point == Point(0, 0)


def test_point_inside_cutoff_code(null_point):
    assert get_code(null_point, [-4, 3, 4, -2]) == 0


def test_point_outside_cutoff_code(null_point):
    assert get_code(null_point, [-4, -3, -4, -2]) == 5


def test_point_on_edge_cutoff_code(null_point):
    assert get_code(null_point, [0, 2, 4, -2]) == 0

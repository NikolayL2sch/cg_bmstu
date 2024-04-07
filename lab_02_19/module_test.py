from matrix_methods import mul_matrices, get_new_coords
from class_point import Point
import pytest


@pytest.fixture
def null_point():
    return Point()


@pytest.fixture
def ed_matrix():
    return [[1, 0, 0], [0, 1, 0], [0, 0, 1]]


def test_zero_point(ed_matrix, null_point):
    assert mul_matrices(ed_matrix, null_point) == null_point


def test_raises_empty_point_list(ed_matrix):
    with pytest.raises(AttributeError):
        get_new_coords([], ed_matrix)

import pytest
from class_point import Point
from paint_algs import get_y_extremum, get_figure_edges, create_empty_linked_list


@pytest.fixture
def null_point():
    return Point()


p1 = [Point(0, 20), Point(1, 2), Point(2, 3)]
p2 = [Point(0, 1), Point(1, -200), Point(0, 0), Point(1, -55)]


def test_get_y_extremum_null(null_point):
    assert get_y_extremum([[null_point], [null_point]]) == (0, 0)


def test_get_y_extremum():
    assert get_y_extremum([p1, p2]) == (-200, 20)


def test_get_figure_edges():
    result = get_figure_edges([p1, p2])
    edges = [[Point(0, 20), Point(1, 2)], [Point(1, 2), Point(2, 3)],
             [Point(2, 3), Point(0, 20)], [Point(0, 1), Point(1, -200)],
             [Point(1, -200), Point(0, 0)], [Point(0, 0), Point(1, -55)],
             [Point(1, -55), Point(0, 1)]]
    for i in range(len(result)):
        for j in range(len(result[i])):
            assert result[i][j] == edges[i][j]


def test_create_empty_linked_list():
    assert (len(create_empty_linked_list(-222.6, 23.3)) == 246)

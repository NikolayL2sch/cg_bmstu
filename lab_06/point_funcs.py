from typing import List

from PyQt5.QtWidgets import QGraphicsLineItem

from class_point import Point


def del_lines_by_point(edges: List[QGraphicsLineItem], ind: int) -> None:
    if len(edges) > 1 and edges[ind - 1]:
        for line in edges[ind - 1]:
            if line in edges[ind]:
                edges[ind - 1].remove(line)
    if len(edges) > 1 and edges[ind + 1]:
        for line in edges[ind + 1]:
            if line in edges[ind]:
                edges[ind + 1].remove(line)


def add_symmetr_points(p1: Point, p2: Point, is_circle=False) -> List[Point]:
    points_list = []
    dx = p2.x - p1.x
    dy = p2.y - p1.y

    if is_circle:
        points_list.append(Point(p1.x - dy, p1.y + dx))
        points_list.append(Point(p1.x + dy, p1.y + dx))
        points_list.append(Point(p1.x + dy, p1.y - dx))
        points_list.append(Point(p1.x - dy, p1.y - dx))

    points_list.append(Point(p1.x - dx, p1.y + dy))
    points_list.append(Point(p1.x + dx, p1.y + dy))
    points_list.append(Point(p1.x + dx, p1.y - dy))
    points_list.append(Point(p1.x - dx, p1.y - dy))

    return points_list

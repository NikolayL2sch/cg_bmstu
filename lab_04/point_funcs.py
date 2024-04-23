from typing import List

from class_point import Point


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

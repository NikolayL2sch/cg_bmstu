from typing import Union, List

from class_point import Point
from point_funcs import add_symmetr_points


def sign(n: Union[int, float]) -> int:
    if n == 0:
        return 0
    if n < 0:
        return -1
    return 1


def brezenhem_circle(p: Point, radius: float) -> List[Point]:
    points = []
    x = 0
    y = radius
    d = 2 * (1 - radius)
    while x <= y:
        points.extend(add_symmetr_points(p, Point(x + p.x, y + p.y), True))
        d1 = 2 * d + 2 * y - 1
        if d1 < 0:
            x += 1
            d = d + 2 * x + 1
        else:
            x += 1
            y -= 1
            d = d + 2 * (x - y + 1)
    return points


def brezenhem_ellipse(p: Point, width: float, height: float) -> List[Point]:
    x = 0
    y = height
    points = []

    d = height * height - width * width * (2 * height - 1)
    y_k = 0
    while y >= y_k:
        points.extend(add_symmetr_points(p, Point(x + p.x, y + p.y)))
        if d <= 0:
            d1 = 2 * d + width * width * (2 * y + 2)
            if d1 < 0:
                x += 1
                d = d + height * height * (2 * x + 1)
            else:
                x += 1
                y -= 1
                d += height * height * (2 * x + 1) + width * width * (1 - 2 * y)
        else:
            d2 = 2 * d + height * height * (2 - 2 * x)
            y -= 1
            if d2 < 0:
                x += 1
                d = d + height * height * \
                    (2 * x + 1) + width * width * (1 - 2 * y)
            else:
                d += width * width * (1 - 2 * y)
    return points


def brezenhem_line(p1: Point, p2: Point) -> List[Point]:
    points = []

    if abs(p1.x - p2.x) <= 1e-13 and abs(p1.y - p2.y) <= 1e-13:
        points.append(Point(p1.x, p1.y))
        return points

    dx = p2.x - p1.x
    dy = p2.y - p1.y
    sx = sign(dx)
    sy = sign(dy)

    dx = abs(dx)
    dy = abs(dy)

    if dy > dx:
        dx, dy = dy, dx
        swap = True
    else:
        swap = False

    f = 2 * dy - dx
    x = p1.x
    y = p1.y
    for i in range(int(dx + 1)):
        points.append(Point(x, y))

        if f >= 0:
            if swap:
                x += sx
            else:
                y += sy
            f -= 2 * dx
        if f <= 0:
            if swap:
                y += sy
            else:
                x += sx
            f += 2 * dy
    return points

from math import floor, fabs
from typing import List, Union, Tuple

from class_point import Point


def sign(n: Union[int, float]) -> int:
    if n == 0:
        return 0
    if n < 0:
        return -1
    return 1


def brezenhem_int(p1: Point, p2: Point) -> List[Point]:
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

    m = dy / dx
    if m > 1:
        dx, dy = dy, dx
        m = 1 / m
        fl = True
    else:
        fl = False

    f = 2 * dy - dx
    x = p1.x
    y = p1.y

    for i in range(1, int(dx + 1)):
        points.append(Point(x, y))
        if f > 0:
            if fl:
                x += sx
            else:
                y += sy
            f -= 2 * dx
        else:
            if fl:
                y += sy
            else:
                x += sx
            f += 2 * dy

    return points


def brezenhem_float(p1: Point, p2: Point) -> List[Point]:
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

    m = dy / dx

    if m > 1:
        dx, dy = dy, dx
        m = 1 / m
        fl = True
    else:
        fl = False

    f = m - 0.5

    x = p1.x
    y = p1.y

    for i in range(1, int(dx + 1)):
        points.append(Point(x, y))
        if f > 0:
            if fl:
                x = x + sx
            else:
                y = y + sy
            f -= 1
        else:
            if fl:
                y = y + sy
            else:
                x = x + sx
            f += m
    return points


def brezenhem_st(p1: Point, p2: Point) -> List[Tuple[Point, float]]:
    points = []

    if abs(p1.x - p2.x) <= 1e-13 and abs(p1.y - p2.y) <= 1e-13:
        points.append((Point(p1.x, p1.y), 255))
        return points

    dx = p2.x - p1.x
    dy = p2.y - p1.y
    sx = sign(dx)
    sy = sign(dy)
    dx = abs(dx)
    dy = abs(dy)
    m = dy / dx
    if m > 1:
        dx, dy = dy, dx
        m = 1 / m
        fl = True
    else:
        fl = False

    intensity = 255
    f = intensity / 2

    x = p1.x
    y = p1.y

    for i in range(1, int(dx + 1)):
        if f < 1 - m:
            if fl:
                y += sy
            else:
                x += sx
            f += m
        else:
            x += sx
            y += sy
            f -= (1 - m)

        points.append((Point(x, y), f))

    return points


def cda(p1: Point, p2: Point) -> List[Point]:
    points = []

    if abs(p1.x - p2.x) <= 1e-13 and abs(p1.y - p2.y) <= 1e-13:
        points.append(Point(p1.x, p1.y))
        return points

    if abs(p2.x - p1.x) > abs(p2.y - p1.y):
        L = abs(p2.x - p1.x)
    else:
        L = abs(p2.y - p1.y)

    dx = (p2.x - p1.x) / L
    dy = (p2.y - p1.y) / L

    x = p1.x
    y = p1.y

    for i in range(1, int(L + 1)):
        points.append(Point(round(x), round(y)))
        x = x + dx
        y = y + dy

    return points


def vu(p1: Point, p2: Point, counting_steps=False) -> List[Tuple[Point, float]]:
    points = []

    count_steps = 0
    if abs(p1.x - p2.x) <= 1e-13 and abs(p1.y - p2.y) <= 1e-13:
        points.append((Point(p1.x, p1.y), 255))
        return points

    dx = p2.x - p1.x
    dy = p2.y - p1.y

    intensity = 1
    step = 1

    if abs(dy) >= abs(dx):
        if dy != 0:
            intensity = dx / dy

        tmp_intensity = intensity

        if p1.y > p2.y:
            tmp_intensity *= -1
            step *= -1

        end = round(p2.y) - 1 if dx > dy else round(p2.y) + 1

        for y in range(round(p1.y), end, step):
            d1 = p1.x - floor(p1.x)
            d2 = 1 - d1

            if not counting_steps:
                points.append((Point(int(p1.x) + 1, y), round(fabs(d1) * 255)))
                points.append((Point(int(p1.x), y), round(fabs(d2) * 255)))
            elif y < round(p2.y) and int(p1.x) != int(p1.x + intensity):
                count_steps += 1

            p1.x += tmp_intensity
    else:
        if dx != 0:
            intensity = dy / dx

        temp_intensity_coefficient = intensity

        if p1.x > p2.x:
            temp_intensity_coefficient *= -1
            step *= -1

        end = round(p2.x) - 1 if dx < dy else round(p2.x) + 1

        for x in range(round(p1.x), end, step):
            d1 = p1.y - floor(p1.y)
            d2 = 1 - d1

            if not counting_steps:
                points.append((Point(x, int(p1.y) + 1), round(fabs(d1) * 255)))
                points.append((Point(x, int(p1.y)), round(fabs(d2) * 255)))
            elif x < round(p2.x) and int(p1.y) != int(p1.y + intensity):
                count_steps += 1

            p1.y += temp_intensity_coefficient

    return points if not counting_steps else count_steps

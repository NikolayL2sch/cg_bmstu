from typing import List, Union

from PyQt5.QtGui import QVector2D

from class_point import Point


def sign(n: Union[int, float]) -> int:
    if abs(n) <= 1e-10:
        return 0
    if n < 0:
        return -1
    return 1


def get_segment_vector(p1: Point, p2: Point) -> QVector2D:
    return QVector2D(p2.x - p1.x, p2.y - p1.y)


def get_vector_mul(v1: QVector2D, v2: QVector2D) -> float:
    return v1.x() * v2.y() - v1.y() * v2.x()


def check_convexity_polygon(figure_point_list: List[Point]) -> bool:
    v1 = get_segment_vector(figure_point_list[0], figure_point_list[1])
    v2 = get_segment_vector(figure_point_list[1], figure_point_list[2])

    if get_vector_mul(v1, v2) > 0:
        s = 1
    else:
        s = -1

    for i in range(len(figure_point_list)):
        v_i = get_segment_vector(
            figure_point_list[i - 2], figure_point_list[i - 1])
        v_j = get_segment_vector(
            figure_point_list[i - 1], figure_point_list[i])

        # если знак произведения хотя бы раз отличается от начального sign, то многоугольник не выпуклый
        if s * get_vector_mul(v_i, v_j) < 0:
            return False

    if s < 0:
        figure_point_list.reverse()

    return True


def visibility(point: Point, begin: Point, end: Point) -> int:
    res = (point.x - begin.x) * (end.y - begin.y) - (point.y - begin.y) * (end.x - begin.x)
    return sign(res)


def check_crossing(seg1_b: Point, seg1_e: Point, seg2_b: Point, seg2_e: Point) -> bool:
    v_1 = visibility(seg1_b, seg2_b, seg2_e)
    v_2 = visibility(seg1_e, seg2_b, seg2_e)

    if v_1 < 0 < v_2 or v_1 > 0 > v_2:
        return True
    return False


def get_cross_point(seg1_b: Point, seg1_e: Point, seg2_b: Point, seg2_e: Point) -> Point:
    def determinant(a, b, c, d):
        return a * d - b * c

    # Matrix k
    a1 = seg1_e.x - seg1_b.x
    b1 = seg2_b.x - seg2_e.x
    a2 = seg1_e.y - seg1_b.y
    b2 = seg2_b.y - seg2_e.y

    # Matrix r
    r1 = seg2_b.x - seg1_b.x
    r2 = seg2_b.y - seg1_b.y

    det_k = determinant(a1, b1, a2, b2)

    inv_k11 = b2 / det_k
    inv_k12 = -b1 / det_k

    # Multiplying inverse of k by r
    p = inv_k11 * r1 + inv_k12 * r2

    # Calculating intersection point
    x = seg1_b.x + a1 * p
    y = seg1_b.y + a2 * p

    return Point(x, y)


def sutherland_hodgman(polygon: List[Point], cutoff: List[Point]) -> List[Point]:
    p = polygon.copy()
    c = cutoff.copy()

    np = len(p)
    nc = len(c)

    f = []
    s = Point()

    for i in range(nc - 1):
        nq = 0
        q = []
        for j in range(np):
            if j != 0:
                is_crossing = check_crossing(s, p[j], c[i], c[i + 1])
                if is_crossing:
                    q.append(get_cross_point(s, p[j], c[i], c[i + 1]))
                    nq += 1
                else:
                    if visibility(s, c[i], c[i + 1]) == 0:
                        q.append(s)
                        nq += 1
                    elif visibility(p[j], c[i], c[i + 1]) == 0:
                        q.append(s)
                        nq += 1
            else:
                f = p[j]
            s = p[j]
            if visibility(s, c[i], c[i + 1]) > 0:
                continue
            q.append(s)
            nq += 1
        if nq == 0:
            continue
        is_crossing = check_crossing(s, f, c[i], c[i + 1])
        if not is_crossing:
            p = q
            np = nq
            continue
        q.append(get_cross_point(s, f, c[i], c[i + 1]))
        nq += 1
        p = q
        np = nq

    return p

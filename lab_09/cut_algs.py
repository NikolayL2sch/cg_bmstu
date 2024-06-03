from typing import List, Tuple, Union

from PyQt5.QtGui import QVector2D

from class_point import Point


def get_segment_vector(p1: Point, p2: Point) -> QVector2D:
    return QVector2D(p2.x - p1.x, p2.y - p1.y)


def get_vector_mul(v1: QVector2D, v2: QVector2D) -> float:
    return v1.x() * v2.y() - v1.y() * v2.x()


def check_convexity_polygon(figure_point_list: List[Point]) -> bool:
    v1 = get_segment_vector(figure_point_list[0], figure_point_list[1])
    v2 = get_segment_vector(figure_point_list[1], figure_point_list[2])

    if get_vector_mul(v1, v2) > 0:
        sign = 1
    else:
        sign = -1

    for i in range(len(figure_point_list)):
        v_i = get_segment_vector(
            figure_point_list[i - 2], figure_point_list[i - 1])
        v_j = get_segment_vector(
            figure_point_list[i - 1], figure_point_list[i])

        # если знак произведения хотя бы раз отличается от начального sign, то многоугольник не выпуклый
        if sign * get_vector_mul(v_i, v_j) < 0:
            return False

    if sign < 0:
        figure_point_list.reverse()

    return True


def get_normal(p1: Point, p2: Point, p3: Point) -> QVector2D:
    vector = get_segment_vector(p1, p2)
    # print(f'segment: {p1.x, p1.y}, {p2.x, p2.y}')
    # print(f'point: {p3.x, p3.y}')
    if vector.y() != 0:
        normal = QVector2D(1, -vector.x() / vector.y())
    else:
        normal = QVector2D(0, 1)

    if QVector2D.dotProduct(get_segment_vector(p2, p3), normal) < 0:
        return -normal

    return normal


def cyrus_beck(p1: Point, p2: Point, figure_point_list: List[Point]) -> Union[Tuple[Point, Point], None]:
    # параметр параметрического уравнения отрезка
    t_beg = 0
    t_end = 1
    # вектор, задающий ориентацию отсекаемого отрезка
    d = get_segment_vector(p1, p2)
    for i in range(-2, len(figure_point_list) - 2):
        # Вычисление вектора внутренней нормали к очередной i-ой стороне окна отсечения
        normal = get_normal(
            figure_point_list[i], figure_point_list[i + 1], figure_point_list[i + 2])
        # print(f'inner normal: {normal.x(), normal.y()}')
        w = get_segment_vector(figure_point_list[i], p1)

        d_i = QVector2D.dotProduct(d, normal)
        w_i = QVector2D.dotProduct(w, normal)

        if d_i == 0:
            if w_i >= 0:
                continue
            else:
                return

        t = - w_i / d_i

        if d_i > 0:
            if t > 1:
                return
            else:
                t_beg = max(t_beg, t)
        else:
            if t < 0:
                return
            else:
                t_end = min(t_end, t)

    if t_beg <= t_end:
        dot1_res = Point(p1.x + d.x() * t_beg, p1.y + d.y() * t_beg)
        dot2_res = Point(p1.x + d.x() * t_end, p1.y + d.y() * t_end)

        return dot1_res, dot2_res

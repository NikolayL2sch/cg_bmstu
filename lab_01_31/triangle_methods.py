from math import acos, degrees
from typing import List, Union, Tuple

from PyQt5.QtGui import QVector2D

from class_point import EPS, Point
from dialogs import show_err_win


def check_one_line(point_list: List[Point]) -> bool:
    half_area = point_list[0].x * (point_list[1].y - point_list[2].y) + \
                point_list[1].x * (point_list[2].y - point_list[0].y) + \
                point_list[2].x * (point_list[0].y - point_list[1].y)
    if abs(half_area) < EPS:
        return True
    return False


def find_min_angle(point_list: List[Point]) -> Union[Tuple[List[float], QVector2D, QVector2D, float], None]:
    min_angle = 180
    ans_vertex = []
    v_p, v_m = None, None

    if not point_list or len(point_list) < 3:
        show_err_win("Недостаточно точек для решения задачи.\nДобавьте хотя бы 3 точки.")
        return
    if check_one_line(point_list):
        show_err_win("Невозможно построить треугольник.\nТочки лежат на одной прямой.")
        return

    for i in range(len(point_list) - 2):
        for j in range(i + 1, len(point_list) - 1):
            for k in range(j + 1, len(point_list)):
                pa = point_list[i]
                pb = point_list[j]
                pc = point_list[k]

                v_a = QVector2D(pa.x, pa.y)
                v_b = QVector2D(pb.x, pb.y)
                v_c = QVector2D(pc.x, pc.y)

                side_v_1 = v_b - v_a
                side_v_2 = v_c - v_b
                side_v_3 = v_c - v_a

                if not is_triangle(side_v_1, side_v_2, side_v_3):
                    continue
                # print(f'Sides OX: {side_v_1.x()}, {side_v_2.x()}, {side_v_3.x()}')
                # print(f'Sides OY: {side_v_1.y()}, {side_v_2.y()}, {side_v_3.y()}')
                vm_i, vp_i, angle_i = find_corner(side_v_1, side_v_3, side_v_2)
                vm_j, vp_j, angle_j = find_corner(-side_v_1, side_v_2, side_v_3)
                vm_k, vp_k, angle_k = find_corner(-side_v_3, -side_v_2, side_v_1)

                cur_min_angle = min(angle_i, angle_j, angle_k)
                if min_angle > cur_min_angle:
                    min_angle = cur_min_angle
                    if abs(angle_i - min_angle) < EPS:
                        v_p = vp_i
                        v_m = vm_i
                        ans_vertex = [pa, pb, pc]
                    if abs(angle_j - min_angle) < EPS:
                        v_p = vp_j
                        v_m = vm_j
                        ans_vertex = [pb, pa, pc]
                    if abs(angle_k - min_angle) < EPS:
                        v_p = vp_k
                        v_m = vm_k
                        ans_vertex = [pc, pa, pb]
    return ans_vertex, v_p, v_m, min_angle


def is_triangle(v1: QVector2D, v2: QVector2D, v3: QVector2D) -> bool:
    len_v1 = v1.length()
    len_v2 = v2.length()
    len_v3 = v3.length()

    if abs(len_v1 + len_v2 - len_v3) < EPS or abs(len_v2 + len_v3 - len_v1) < EPS or abs(
            len_v1 + len_v3 - len_v2) < EPS:
        return False
    return True


def find_corner(v1: QVector2D, v2: QVector2D, v3: QVector2D) -> Tuple[QVector2D, QVector2D, float]:
    perpend = find_intersection_altitude(v2, v3)
    median = (v1 + v2) / 2

    # print(f'Perpend x: {perpend.x()}, y: {perpend.y()}\nMedian x: {median.x()}, y: {median.y()}')

    return perpend, median, count_corner(perpend, median)


def count_corner(v1: QVector2D, v2: QVector2D) -> float:
    dot_product = QVector2D.dotProduct(v1, v2)
    magnitude_product = v1.length() * v2.length()

    angle_radians = acos(dot_product / magnitude_product)
    angle_degrees = degrees(angle_radians)

    return angle_degrees


def find_intersection_altitude(v2, v3):
    proj = QVector2D.dotProduct(v2, v3) / (v3.length() ** 2) * v3
    v_height = v2 - proj
    return v_height

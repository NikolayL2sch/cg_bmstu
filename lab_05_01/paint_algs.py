import time
from copy import copy
from typing import List, Tuple, Dict

from PyQt5.QtCore import QEventLoop
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsLineItem, QGraphicsScene, QMainWindow, QApplication

from class_node import Node
from class_point import Point


def get_figure_edges(figures: List[List[Point]]) -> List[List[Point]]:
    edges = []
    for figure in figures:
        for _ in range(len(figure)):
            if _ + 1 > len(figure) - 1:
                edges.append([figure[-1], figure[0]])
            else:
                edges.append([figure[_], figure[_ + 1]])
    return edges


def get_y_extremum(figures: List[List[Point]]) -> Tuple[float, float]:
    y_min = figures[0][0].y
    y_max = figures[0][0].y
    for figure in figures:
        for point in figure:
            if point.y > y_max:
                y_max = point.y
            if point.y < y_min:
                y_min = point.y
    return y_min, y_max


def create_empty_linked_list(y_min: float, y_max: float) -> Dict:
    linked_list = {}
    for _ in range(round(y_max), round(y_min), -1):
        linked_list[_] = []
    return linked_list


def fill_in_nodes(y_groups: Dict, p0: Point, p1: Point) -> None:
    if p0.y > p1.y:
        p1.x, p0.x = p0.x, p1.x
        p1.y, p0.y = p0.y, p1.y

    y_p = p1.y - p0.y

    if y_p != 0:
        x_step = -(p1.x - p0.x) / y_p
        if p1.y not in y_groups:
            y_groups[p1.y] = [Node(p1.x, x_step, y_p)]
        else:
            y_groups[p1.y].append(Node(p1.x, x_step, y_p))


def iter_active_edges(active_edges: List[Node]) -> None:
    i = 0
    while i < len(active_edges):
        active_edges[i].x += active_edges[i].dx
        active_edges[i].dy -= 1
        if active_edges[i].dy < 1:
            active_edges.pop(i)
        else:
            i += 1


def append_active_edges(y_groups: Dict, active_edges: List[Node], y: float) -> None:
    if y in y_groups:
        for y_group in y_groups.get(y):
            active_edges.append(y_group)
    active_edges.sort(key=lambda edge: edge.x)


def draw_curr_scan_string(scene: QGraphicsScene, active_edges: List[Point], y: float, color: QColor) -> None:
    for i in range(0, len(active_edges), 2):
        try:
            line = QGraphicsLineItem(active_edges[i].x, -y, active_edges[i + 1].x, -y)
            line.setPen(color)
            line.setZValue(1)
            scene.addItem(line)
        except IndexError:
            line = QGraphicsLineItem(active_edges[i].x, -y, active_edges[i - 1].x, -y)
            line.setPen(color)
            line.setZValue(1)
            scene.addItem(line)


def paint_alg(figures: List[List[Point]], win: QMainWindow, color: QColor, test_i: int, delay=False, func_testing=False) -> List[Point]:
    y_min, y_max = get_y_extremum(figures)
    edges = get_figure_edges(figures)
    y_groups = create_empty_linked_list(y_min, y_max)

    for edge in edges:
        fill_in_nodes(y_groups, copy(edge[0]), copy(edge[1]))

    y_start = y_min
    y_end = y_max
    active_edges = []
    if func_testing:
        step_screenshot = abs(y_end - y_start) // 7
        start = 0
        screenshot_i = 0
    while y_end > y_start:
        iter_active_edges(active_edges)
        append_active_edges(y_groups, active_edges, y_end)
        draw_curr_scan_string(win.scene, active_edges, y_end, color)
        y_end -= 1
        if delay:
            if func_testing:
                if start == step_screenshot:
                    screenshot = win.grab()
                    screenshot.save(f'./results/test_delay_{test_i}_{screenshot_i}.png', 'png')
                    start = 0
                    screenshot_i += 1
                start += 1
            QApplication.processEvents(QEventLoop.AllEvents, 1)
            time.sleep(0.01)

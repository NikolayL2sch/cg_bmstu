import sys
from time import time

from typing import List

from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsTextItem, QColorDialog
from PyQt5.QtGui import QWheelEvent, QMouseEvent, QPen, QColor, QKeyEvent

from dialogs import show_author, show_task, show_instruction, show_war_win
from class_point import Point
from equations import get_equations

max_win_size: List[int] = [0, 0, 0]

scale: float = 1.0

is_pressed: bool = False
dragging: bool = False

last_pos: QPoint = None
current_color: QColor = QColor(255, 0, 0)

equations, equations_str = get_equations()


def change_polygon_color() -> None:
    colour = QColorDialog.getColor(initial=current_polygon_color)
    if colour.isValid():
        if colour.getRgb() != current_cutoff_figure_color.getRgb():
            set_polygon_color(QColor(colour))
        else:
            show_war_win(
                "Цвет отсекателя и отсекаемого многоугольника не могут совпадать.")


def set_polygon_color(color: QColor) -> None:
    global current_polygon_color
    current_polygon_color = color


def set_cutoff_color(color: QColor) -> None:
    global current_cutoff_figure_color
    current_cutoff_figure_color = color


def change_cutoff_color() -> None:
    colour = QColorDialog.getColor(initial=current_cutoff_figure_color)
    if colour.isValid():
        if colour.getRgb() != current_polygon_color.getRgb():
            set_cutoff_color(QColor(colour))
        else:
            show_war_win("Цвет отсекателя и отрезков не могут совпадать.")


def connect_to_edge(item):
    global pinned_edge
    global enter_pinned_point
    enter_pinned_point = True if not enter_pinned_point else False
    unpacked_segment = item.text().split(' <-> ')
    p1_str = unpacked_segment[0][1:-1].split(',')
    p2_str = unpacked_segment[1][1:-1].split(',')
    pinned_edge = [Point(float(p1_str[0]), float(p1_str[1])),
                   Point(float(p2_str[0]), float(p2_str[1]))]


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("./template.ui", self)  # временно в корне

        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)

        self.need_grid()

        self.add_grid()

        # menu bar
        self.about_author.triggered.connect(show_author)
        self.about_task.triggered.connect(show_task)
        self.instruction.triggered.connect(show_instruction)

        self.clear_button.clicked.connect(self.clear_scene)

        self.graphicsView.setMouseTracking(True)

        # push buttons
        self.add_cutoff_button.clicked.connect(self.add_cutoff)
        self.change_cutoff_color_button.clicked.connect(change_cutoff_color)
        self.change_polygon_color_button.clicked.connect(change_polygon_color)
        self.cutoff_button.clicked.connect(self.cutoff)
        self.close_figure_button.clicked.connect(self.close_figure)

        # graphics view mouse events
        self.graphicsView.mousePressEvent = self.mousePressEvent
        self.graphicsView.wheelEvent = self.wheel_event
        self.graphicsView.mouseReleaseEvent = self.mouseReleaseEvent
        self.graphicsView.mouseMoveEvent = self.mouseMoveEvent

        # QListWidget events
        self.edges_list.itemClicked.connect(connect_to_edge)

        self.show()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        global is_pressed, dragging
        if event.button() == Qt.LeftButton:
            dragging = False
            is_pressed = False

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        global last_pos, dragging
        if is_pressed:
            dragging = True
            dx = event.pos().x() - last_pos.x()
            dy = event.pos().y() - last_pos.y()
            self.graphicsView.horizontalScrollBar().setValue(
                self.graphicsView.horizontalScrollBar().value() - dx)
            self.graphicsView.verticalScrollBar().setValue(
                self.graphicsView.verticalScrollBar().value() - dy)
            last_pos = event.pos()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        global last_pos, is_pressed
        if event.button() == Qt.LeftButton:
            is_pressed = True
            last_pos = event.pos()

    def change_color(self, color: QColor) -> None:
        global current_polygon_color
        current_polygon_color = color
        objects = self.scene.items()
        for obj in objects:
            if obj not in grid_lines and not isinstance(obj, QGraphicsTextItem):
                obj.setPen(current_polygon_color)

    def clear_scene(self):
        pass

    def set_new_colour(self) -> None:
        colour = QColorDialog.getColor(initial=current_polygon_color)
        if colour.isValid():
            self.change_color(QColor(colour))


if __name__ == '__main__':
    global test_i
    start_testing = time()
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()

    FUNC_TESTING = False
    if len(sys.argv) > 2:
        FUNC_TESTING = True
        test_i = int(sys.argv[1])

    if FUNC_TESTING:
        screenshot = window.grab()
        screenshot.save(f'./results/test_{test_i}.png', 'png')
    else:
        sys.exit(app.exec_())

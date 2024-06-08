import sys
from time import time

from typing import List

from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsTextItem, QColorDialog
from PyQt5.QtGui import QWheelEvent, QMouseEvent, QColor

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


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("./lab_10/template.ui", self)  # временно в корне

        for _ in equations_str:
            self.set_cur_equation.addItem(_)

        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)

        # menu bar
        self.about_author.triggered.connect(show_author)
        self.about_task.triggered.connect(show_task)
        self.instruction.triggered.connect(show_instruction)

        self.clear_button.clicked.connect(self.clear_scene)

        self.graphicsView.setMouseTracking(True)

        # push buttons
        # graphics view mouse events
        self.graphicsView.mousePressEvent = self.mousePressEvent
        self.graphicsView.wheelEvent = self.wheel_event
        self.graphicsView.mouseReleaseEvent = self.mouseReleaseEvent
        self.graphicsView.mouseMoveEvent = self.mouseMoveEvent

        self.show()

    def wheel_event(self, event: QWheelEvent) -> None:
        global scale
        factor = 1.2

        if event.angleDelta().y() > 0:
            self.graphicsView.scale(factor, factor)
        else:
            self.graphicsView.scale(1.0 / factor, 1.0 / factor)

        # Получаем текущий масштаб по оси X (и Y)
        scale = self.graphicsView.transform().m11()

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

    def show_current_index(self):
        current_index = self.set_cur_equation.currentIndex()
        print(f"Current index: {current_index}")


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
        window.show_current_index()
        sys.exit(app.exec_())

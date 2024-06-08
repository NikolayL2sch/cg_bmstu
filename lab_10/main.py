import sys
from time import time

from typing import List, Callable

from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QGraphicsScene, QColorDialog
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

angles: List[float] = []

def change_color() -> None:
    global current_color
    colour = QColorDialog.getColor(initial=current_color)
    if colour.isValid():
        current_color = colour


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

        # push buttons
        self.change_color_button.clicked.connect(change_color)
        self.draw_graph_button.clicked.connect(self.get_rotate_params)

        # QComboBox events
        self.set_rotate_x.valueChanged.connect(self.rotate_graph)
        self.set_rotate_y.valueChanged.connect(self.rotate_graph)
        self.set_rotate_z.valueChanged.connect(self.rotate_graph)

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

    def clear_scene(self):
        self.scene.clear()

    def get_angles(self):
        return [self.set_rotate_x.value(), self.set_rotate_y.value(), self.set_rotate_z.value()]

    def get_rotate_params(self) -> None:
        global angles
        self.clear_scene()
        angles = self.get_angles()
        x_left = self.set_limit_x1.value()
        z_left = self.ui.set_limit_z1.value()
        x_right = self.set_limit_x2.value()
        z_right = self.set_limit_z2.value()
        delta_x = self.set_step_x.value()
        delta_z = self.set_step_z.value()
        data_x = [x_left, x_right, delta_x]
        data_z = [z_left, z_right, delta_z]
        f = equations[self.ui.FuncOptions.currentIndex()]
        self.draw_graph(data_x, data_z, f)

    def draw_graph(self, data_x: List[float], data_z: List[float], f: Callable[..., float]) -> None:
        pass


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

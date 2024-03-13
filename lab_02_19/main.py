import sys
from typing import List

from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtWidgets import QGraphicsScene

from dialogs import show_author, show_task, show_instruction
from input_checks import params_to_float
from class_point import Point
from matrix_methods import get_new_coords

hyperbole_points: List[Point] = []
circle_points: List[Point] = []
intersection_points: List[Point] = []


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("./lab_02_19/template.ui", self)

        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)

        # menu bar
        self.about_author.triggered.connect(show_author)
        self.about_task.triggered.connect(show_task)
        self.instruction.triggered.connect(show_instruction)

        self.move_action_button.clicked.connect(self.move_figure)
        self.scale_action_button.clicked.connect(self.scale_figure)

        self.show()

    def get_move_params(self) -> float:
        dx_str = self.set_dx.text()
        dy_str = self.set_dy.text()

        params = params_to_float(dx_str, dy_str)

        if len(params) == 0:
            return
        dx, dy = params

        return dx, dy

    def move_figure(self) -> None:
        global hyperbole_points, circle_points, intersection_points

        dx, dy = self.get_move_params()
        print(dx, dy)

        move_matrix = [[1, 0, dx], [0, 1, dy], [0, 0, 1]]

        hyperbole_points = get_new_coords(move_matrix, hyperbole_points)
        circle_points = get_new_coords(move_matrix, circle_points)
        intersection_points = get_new_coords(move_matrix, intersection_points)
        self.draw_figure()

    def draw_figure(self) -> None:
        pass

    def get_scale_params(self) -> float:
        kx_str = self.set_kx.text()
        ky_str = self.set_ky.text()
        cx_str = self.set_cx.text()
        cy_str = self.set_cy.text()

        params = params_to_float(kx_str, ky_str, cx_str, cy_str)

        if len(params) == 0:
            return
        kx, ky, cx, cy = params

        return kx, ky, cx, cy

    def scale_figure(self) -> None:
        global hyperbole_points, circle_points, intersection_points

        kx, ky, cx, cy = self.get_scale_params()
        print(kx, ky, cx, cy)

        move_matrix = [[1, 0, -cx], [0, 1, -cy], [0, 0, 1]]
        scale_matrix = [[kx, 0, 0], [0, ky, 0], [0, 0, 1]]
        move_matrix_back = [[1, 0, cx], [0, 1, cy], [0, 0, 1]]

        hyperbole_points = get_new_coords(move_matrix, hyperbole_points)
        circle_points = get_new_coords(move_matrix, circle_points)
        intersection_points = get_new_coords(move_matrix, intersection_points)

        hyperbole_points = get_new_coords(scale_matrix, hyperbole_points)
        circle_points = get_new_coords(scale_matrix, circle_points)
        intersection_points = get_new_coords(scale_matrix, intersection_points)

        hyperbole_points = get_new_coords(move_matrix_back, hyperbole_points)
        circle_points = get_new_coords(move_matrix_back, circle_points)
        intersection_points = get_new_coords(move_matrix_back, intersection_points)
        self.draw_figure()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()

import sys
from time import time
from math import radians, cos, sin
from matplotlib import pyplot

from typing import List, Tuple, Union

from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsLineItem, QButtonGroup, QGraphicsRectItem
from PyQt5.QtGui import QWheelEvent, QMouseEvent, QPen, QColor, QBrush

from dialogs import show_author, show_task, show_instruction
from class_point import Point
from input_checks import params_to_float
from point_algs import brezenhem_float, brezenhem_st, brezenhem_int, cda, vu

grid_lines: List[QGraphicsLineItem] = []
max_win_size: List[int] = [0, 0, 0]

scale: float = 1.0
num_tests: int = 50

is_pressed: bool = False

last_pos: QPoint = None
current_line_color: QColor = QColor(255, 0, 0)


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("./out/template.ui", self)  # временно в корне

        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.need_grid()
        self.add_grid()

        # menu bar
        self.about_author.triggered.connect(show_author)
        self.about_task.triggered.connect(show_task)
        self.instruction.triggered.connect(show_instruction)

        # add button group so that other will stay unchecked
        self.line_color_group = QButtonGroup()
        self.bg_color_group = QButtonGroup()
        self.alg_group = QButtonGroup()

        self.line_color_group.addButton(self.blue_line_rbutton)
        self.line_color_group.addButton(self.red_line_rbutton)
        self.line_color_group.addButton(self.green_line_rbutton)
        self.line_color_group.addButton(self.aqua_line_rbutton)
        self.line_color_group.addButton(self.purple_line_rbutton)
        self.line_color_group.addButton(self.yellow_line_rbutton)

        self.bg_color_group.addButton(self.blue_bg_rbutton)
        self.bg_color_group.addButton(self.red_bg_rbutton)
        self.bg_color_group.addButton(self.green_bg_rbutton)
        self.bg_color_group.addButton(self.aqua_bg_rbutton)
        self.bg_color_group.addButton(self.purple_bg_rbutton)
        self.bg_color_group.addButton(self.gray_bg_rbutton)

        self.alg_group.addButton(self.brezenhem_float_rbutton)
        self.alg_group.addButton(self.brezenhem_int_rbutton)
        self.alg_group.addButton(self.brezenhem_st_rbutton)
        self.alg_group.addButton(self.cda_alg_rbutton)
        self.alg_group.addButton(self.vu_alg_rbutton)
        self.alg_group.addButton(self.bibl_alg_rbutton)

        # !!! radio buttons setChecked (setup default config)
        self.red_line_rbutton.setChecked(True)
        self.gray_bg_rbutton.setChecked(True)
        self.bibl_alg_rbutton.setChecked(True)

        # line color radio buttons
        self.blue_line_rbutton.clicked.connect(
            lambda: self.set_lines_color(Qt.blue))
        self.red_line_rbutton.clicked.connect(
            lambda: self.set_lines_color(Qt.red))
        self.green_line_rbutton.clicked.connect(
            lambda: self.set_lines_color(Qt.darkGreen))
        self.aqua_line_rbutton.clicked.connect(
            lambda: self.set_lines_color(Qt.darkCyan))
        self.purple_line_rbutton.clicked.connect(
            lambda: self.set_lines_color(Qt.darkMagenta))
        self.yellow_line_rbutton.clicked.connect(
            lambda: self.set_lines_color(Qt.darkYellow))

        # background color radio buttons
        self.blue_bg_rbutton.clicked.connect(
            lambda: self.set_bg_color(Qt.blue))
        self.red_bg_rbutton.clicked.connect(lambda: self.set_bg_color(Qt.red))
        self.green_bg_rbutton.clicked.connect(
            lambda: self.set_bg_color(Qt.darkGreen))
        self.aqua_bg_rbutton.clicked.connect(
            lambda: self.set_bg_color(Qt.darkCyan))
        self.purple_bg_rbutton.clicked.connect(
            lambda: self.set_bg_color(Qt.darkMagenta))
        self.gray_bg_rbutton.clicked.connect(
            lambda: self.set_bg_color(QColor(56, 56, 56)))

        self.ladder_test_button.clicked.connect(self.ladder_test)
        self.time_test_button.clicked.connect(self.time_test)

        self.draw_segment_button.clicked.connect(self.draw_segment)
        self.draw_spektr_button.clicked.connect(self.draw_spectre)
        self.clear_button.clicked.connect(self.clear_scene)

        self.graphicsView.setMouseTracking(True)

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
        if self.need_grid():
            for grid_line in grid_lines:
                if grid_line in self.scene.items():
                    self.scene.removeItem(grid_line)
            self.add_grid()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        global is_pressed
        if event.button() == Qt.LeftButton:
            is_pressed = False

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        global last_pos
        if is_pressed:
            dx = event.pos().x() - last_pos.x()
            dy = event.pos().y() - last_pos.y()
            self.graphicsView.horizontalScrollBar().setValue(
                self.graphicsView.horizontalScrollBar().value() - dx)
            self.graphicsView.verticalScrollBar().setValue(
                self.graphicsView.verticalScrollBar().value() - dy)
            last_pos = event.pos()
            if self.need_grid():
                for grid_line in grid_lines:
                    if grid_line in self.scene.items():
                        self.scene.removeItem(grid_line)
                self.add_grid()
        scene_pos = self.graphicsView.mapToScene(event.pos())
        self.current_coords_label.setText(
            f'x :{scene_pos.x():.2f}, y :{-scene_pos.y():.2f}')

    def mousePressEvent(self, event: QMouseEvent) -> None:
        global last_pos, is_pressed
        if event.button() == Qt.LeftButton:
            is_pressed = True
            last_pos = event.pos()

    def need_grid(self) -> bool:
        global max_win_size
        flag: bool = False
        max_size = self.graphicsView.maximumSize()
        max_width = int(max_size.width() * (1 / scale))
        max_height = int(max_size.height() * (1 / scale))
        grid_interval = int(50 * (1 / scale))
        grid_interval = round(grid_interval / 50) * 50
        if grid_interval != max_win_size[2]:
            max_win_size[2] = grid_interval
            flag = True
        if max_win_size[0] < max_width and max_win_size[1] < max_height:
            max_win_size[0] = max_width
            max_win_size[1] = max_height
            flag = True
        return flag

    def add_grid(self) -> None:
        global grid_lines, max_win_size
        max_width = max_win_size[0]
        max_height = max_win_size[1]
        grid_interval = max_win_size[2]
        if grid_interval == 0:
            grid_interval = 20
        self.current_grid_label.setText(f'Текущий шаг сетки: {grid_interval}')
        start_grid_width = - ((max_width // 2) +
                              grid_interval - (max_width // 2) % grid_interval)
        start_grid_height = - \
            ((max_height // 2) + grid_interval - (max_height // 2) % grid_interval)
        end_grid_width = (max_width // 2) - (max_width // 2) % grid_interval
        end_grid_height = (max_height // 2) - (max_width // 2) % grid_interval
        pen = QPen(Qt.darkGray)
        pen_width = 1 if int(1 / scale) == 0 else int(1 / scale)
        pen.setWidth(pen_width)
        for x in range(start_grid_width, end_grid_width, grid_interval):
            line = QGraphicsLineItem(x, start_grid_height, x, end_grid_height)
            line.setPen(pen)
            line.setZValue(0)
            grid_lines.append(line)
            self.scene.addItem(line)
        for y in range(start_grid_height, end_grid_height, grid_interval):
            line = QGraphicsLineItem(start_grid_width, y, end_grid_width, y)
            line.setPen(pen)
            line.setZValue(0)
            grid_lines.append(line)
            self.scene.addItem(line)

        axis_x = QGraphicsLineItem(-300 * (1 / scale), 0, 300 * (1 / scale), 0)
        axis_y = QGraphicsLineItem(0, -300 * (1 / scale), 0, 300 * (1 / scale))
        pen.setColor(Qt.white)
        grid_lines.append(axis_x)
        grid_lines.append(axis_y)
        axis_x.setPen(pen)
        axis_y.setPen(pen)
        axis_x.setZValue(0)
        axis_y.setZValue(0)
        self.scene.addItem(axis_x)
        self.scene.addItem(axis_y)

    def set_lines_color(self, color: QColor) -> None:
        global current_line_color
        current_line_color = color
        lines = self.scene.items()
        for line in lines:
            if line not in grid_lines:
                line.setPen(current_line_color)

    def set_bg_color(self, color: QColor) -> None:
        background_brush = QBrush(color)
        self.graphicsView.setBackgroundBrush(background_brush)

    def clear_scene(self):
        for item in self.scene.items():
            if item not in grid_lines:
                self.scene.removeItem(item)

    def get_segment_coords(self) -> Tuple[Point, Point]:
        x_1_str = self.set_x1.text()
        y_1_str = self.set_y1.text()
        x_2_str = self.set_x2.text()
        y_2_str = self.set_y2.text()
        params = params_to_float(x_1_str, y_1_str, x_2_str, y_2_str)

        if len(params) == 0:
            return

        x1, y1, x2, y2 = params

        return Point(x1, y1), Point(x2, y2)

    def draw_segment(self, p1: Point = None, p2: Point = None) -> None:
        if p1 is None or p2 is None:
            params = self.get_segment_coords()

            if params is None:
                return

            p1, p2 = params

        current_points = self.get_points(p1, p2)
        if not current_points:
            return

        if type(current_points[0]) is Point:
            for point in current_points:
                part = QGraphicsRectItem(point.x, -point.y, 1, 1)
                part.setZValue(1)
                part.setPen(current_line_color)
                self.scene.addItem(part)
        elif type(current_points[0]) is tuple:
            for i in range(len(current_points)):
                point = current_points[i][0]
                intensity = current_points[i][1]

                part = QGraphicsRectItem(point.x, -point.y, 1, 1)
                part.setZValue(1)
                part_color = QColor(current_line_color)
                part_color.setAlpha(int(intensity))
                part.setPen(part_color)
                self.scene.addItem(part)

    def draw_spectre(self, center: Point = None, angle: float = None, length: float = None) -> None:
        if center is None or angle is None or length is None:
            params = self.get_spectre_coeff()
            if params is None:
                return

            center, angle, length = params

        cur_angle = 0

        while cur_angle < 360:
            self.draw_segment(Point(center.x, center.y), Point(center.x + length * cos(radians(cur_angle)),
                                                               center.y + length * sin(radians(cur_angle))))
            cur_angle += angle

    def get_spectre_coeff(self) -> Union[Tuple[Point, float, float], None]:
        x_c_str = self.set_xc.text()
        y_c_str = self.set_yc.text()
        angle_str = self.set_angle.text()
        length_str = self.set_length.text()

        params = params_to_float(x_c_str, y_c_str, angle_str, length_str)

        if len(params) == 0:
            return

        x_c, y_c, angle, length = params

        return Point(x_c, y_c), angle, length

    def get_points(self, p1: Point, p2: Point) -> Union[List[Point], List[Tuple[Point, float]]]:
        if self.brezenhem_int_rbutton.isChecked():
            return brezenhem_int(p1, p2)
        elif self.brezenhem_float_rbutton.isChecked():
            return brezenhem_float(p1, p2)
        elif self.brezenhem_st_rbutton.isChecked():
            return brezenhem_st(p1, p2)
        elif self.cda_alg_rbutton.isChecked():
            return cda(p1, p2)
        elif self.vu_alg_rbutton.isChecked():
            return vu(p1, p2)
        elif self.bibl_alg_rbutton.isChecked():
            line = QGraphicsLineItem(p1.x, -p1.y, p2.x, -p2.y)
            line.setPen(current_line_color)
            line.setZValue(1)
            self.scene.addItem(line)
            return []

    def ladder_test(self, *args):
        if isinstance(args[0], bool):
            params = self.get_spectre_coeff()
            if params is None:
                return
            point, angle, length = params
        else:
            x, y, angle, length = args
            point = Point(x, y)

        steps = [[] for _ in range(5)]
        step = 5
        cur_angle = 0

        while cur_angle < 90:
            for i, alg in enumerate([cda, brezenhem_float, brezenhem_int, brezenhem_st, vu]):
                cur_steps = alg(Point(point.x, point.y), Point(point.x + length * cos(radians(cur_angle)),
                                                               point.y + length * sin(radians(cur_angle))), True)
                steps[i].append(cur_steps)

            cur_angle += step

        pyplot.figure(figsize=(20, 20))
        pyplot.title(f"Сравнение ступенчатости алгоритмов при разных углах, длина: {length}")
        pyplot.xlabel("Угол, °")
        pyplot.ylabel("Кол-во ступенек")

        pyplot.plot([_ for _ in range(0, 90, step)], steps[0], "*", label="ЦДА")
        pyplot.plot([_ for _ in range(0, 90, step)], steps[1], "-.", label="Брезенхем float")
        pyplot.plot([_ for _ in range(0, 90, step)], steps[2], "-", label="Брезенхем int")
        pyplot.plot([_ for _ in range(0, 90, step)], steps[3], ":", label="Брезенхем (сглаживание)")
        pyplot.plot([_ for _ in range(0, 90, step)], steps[4], "--", label="Ву")

        pyplot.xticks([_ for _ in range(0, 91, step)])
        pyplot.legend()

        if not FUNC_TESTING:
            pyplot.show()
        else:
            pyplot.savefig(f'./results/ladder_test_{test_i}.png')

    def time_test(self, *args):
        if isinstance(args[0], bool):
            params = self.get_spectre_coeff()
            if params is None:
                return

            point, angle, length = params
        else:
            x, y, angle, length = args
            point = Point(x, y)

        run_times = []
        for alg in [brezenhem_int, brezenhem_float, brezenhem_st, cda, vu]:
            sum_time = 0

            for _ in range(num_tests):
                start = time()
                cur_angle = 0
                while cur_angle < 360:
                    alg(point, Point(point.x + length * cos(radians(cur_angle)),
                                     point.y + length * sin(radians(cur_angle))))
                    cur_angle += angle
                sum_time += time() - start

            run_times.append(sum_time / num_tests)

        pyplot.figure(figsize=(20, 20))
        pyplot.title("Сравнение времени работы алгоритмов")
        pyplot.xlabel("Название алгоритма")
        pyplot.ylabel("Время, с")
        pyplot.bar(["Брезенхем int", "Брезенхем float", "Брезенхем с устранением ступенчатости", "ЦДА", "Ву"],
                   run_times, color='green')
        if not FUNC_TESTING:
            pyplot.show()
        else:
            pyplot.savefig(f'./results/time_test_{test_i}.png')


if __name__ == '__main__':
    global test_i
    start_testing = time()
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()

    FUNC_TESTING = False
    if len(sys.argv) > 7:
        FUNC_TESTING = True
        test_i = int(sys.argv[1])
        if sys.argv[7] == 'br_int':
            window.brezenhem_int_rbutton.setChecked(True)
        elif sys.argv[7] == 'br_float':
            window.brezenhem_float_rbutton.setChecked(True)
        elif sys.argv[7] == 'cda':
            window.cda_alg_rbutton.setChecked(True)
        elif sys.argv[7] == 'vu':
            window.vu_alg_rbutton.setChecked(True)
        elif sys.argv[7] == 'bibl':
            window.bibl_alg_rbutton.setChecked(True)
        elif sys.argv[7] == 'br_st':
            window.brezenhem_st_rbutton.setChecked(True)

        if sys.argv[2] == 'segment':
            x_1 = float(sys.argv[3])
            y_1 = float(sys.argv[4])
            x_2 = float(sys.argv[5])
            y_2 = float(sys.argv[6])

            window.draw_segment(Point(x_1, y_1), Point(x_2, y_2))

        elif sys.argv[2] == 'spectre':
            xc_ = float(sys.argv[3])
            yc_ = float(sys.argv[4])
            angle_ = float(sys.argv[5])
            length_ = float(sys.argv[6])

            if sys.argv[7] == 'time_test':
                window.time_test(xc_, yc_, angle_, length_)
            elif sys.argv[7] == 'ladder_test':
                window.ladder_test(xc_, yc_, angle_, length_)
            else:
                window.draw_spectre(Point(xc_, yc_), angle_, length_)

    if FUNC_TESTING:
        screenshot = window.grab()
        screenshot.save(f'./results/test_{test_i}.png', 'png')
        time_elapsed = (time() - start_testing) * 1000
        with open('report-functesting-latest.txt', 'a+') as f:
            f.write(f'{test_i}. Time elapsed: {time_elapsed:.2f} mc.\n')
    else:
        sys.exit(app.exec_())

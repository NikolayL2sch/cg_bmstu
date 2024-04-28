import sys
from time import time

from typing import List, Tuple

from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsRectItem, \
    QGraphicsTextItem, QColorDialog
from PyQt5.QtGui import QWheelEvent, QMouseEvent, QPen, QColor, QFont

from dialogs import show_author, show_task, show_instruction, show_err_win, show_war_win
from class_point import Point
from input_checks import params_to_float

grid_lines: List[QGraphicsLineItem] = []
max_win_size: List[int] = [0, 0, 0]
point_list: List[Point] = []
point_scale: List[float] = []
coords_desc: List[QGraphicsTextItem] = []
scene_point_list: List[QGraphicsEllipseItem] = []

scale: float = 1.0
num_tests: int = 50

is_pressed: bool = False
dragging: bool = False

last_pos: QPoint = None
current_line_color: QColor = QColor(255, 0, 0)


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("./lab_05_01/template.ui", self)  # временно в корне

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
        self.add_point_button.clicked.connect(self.add_point)
        self.remove_point_button.clicked.connect(self.remove_point)
        self.change_color_button.clicked.connect(self.set_new_colour)
        self.close_figure_button.clicked.connect(self.close_figure)
        self.paint_figure_button.clicked.connect(self.paint_figure)

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
        for i in range(len(scene_point_list)):
            point = scene_point_list[i]
            point.setTransformOriginPoint(point.boundingRect().center())
            point.setScale(1 / (scale * point_scale[i]))
        if self.need_grid():
            for grid_line in grid_lines:
                if grid_line in self.scene.items():
                    self.scene.removeItem(grid_line)
            self.add_grid()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        global is_pressed, dragging
        if event.button() == Qt.LeftButton:
            if not dragging:
                self.scene.removeItem(self.scene.items()[-1])
                self.add_point_by_click(event)
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
        elif event.button() == Qt.RightButton:
            self.del_point_by_click(event)

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

    def change_color(self, color: QColor) -> None:
        global current_line_color
        print(color)
        current_line_color = color
        objects = self.scene.items()
        cnt = 0
        for obj in objects:
            if obj not in grid_lines:
                print(cnt)
                obj.setPen(current_line_color)
                cnt += 1
                print(cnt)
    def clear_scene(self):
        for item in self.scene.items():
            if item not in grid_lines:
                self.scene.removeItem(item)

    def add_point(self) -> None:
        point = self.get_point_coords()
        if point is not None:
            self.draw_point(point)

    def get_point_coords(self) -> Point:
        x_txt = self.set_x.text()
        y_txt = self.set_y.text()
        params = params_to_float(x_txt, y_txt)
        if params is None:
            return
        x, y = params
        return Point(x, y)

    def add_point_by_click(self, event: QMouseEvent) -> None:
        pos = event.pos()
        scene_pos = self.graphicsView.mapToScene(pos)
        p_x, p_y = scene_pos.x(), scene_pos.y()
        self.draw_point(Point(p_x, -p_y))

    def draw_point(self, point: Point) -> None:
        for _ in point_list:
            if point == _:
                show_war_win("Введенная точка уже существует.")
                break
        else:
            point_list.append(point)
            self.scroll_list.addItem(f'{len(point_list)}.({round(point.x, 2)}; {round(point.y, 2)})')
            point_scale.append(1 / scale)
            point_coords_label = QGraphicsTextItem(f'x:({point.x:.2f}, y:{point.y:.2f})')
            coords_desc.append(point_coords_label)

            point = QGraphicsEllipseItem(point.x, -point.y, 5 * (1 / scale), 5 * (1 / scale))
            point.setBrush(current_line_color)
            self.scene.addItem(point)

            point_coords_label.setPos(point.rect().center().x() + 10, point.rect().center().y())

            point_coords_label.setDefaultTextColor(QColor(255, 255, 255))
            font = QFont()
            font.setPointSize(8)
            point_coords_label.setFont(font)
            point_coords_label.setZValue(1)
            self.scene.addItem(point_coords_label)
            if len(point_list) > 1:
                self.draw_line(point_list[-2], point_list[-1])
            scene_point_list.append(point)

    def draw_line(self, p1: Point, p2: Point) -> None:
        line = QGraphicsLineItem(p1.x, -p1.y, p2.x, -p2.y)
        line.setPen(current_line_color)
        line.setZValue(1)
        self.scene.addItem(line)

    def remove_point(self):
        pass

    def close_figure(self):
        self.draw_line(point_list[0], point_list[-1])

    def paint_figure(self):
        pass

    def del_point_by_click(self, event: QMouseEvent):
        pass

    def set_new_colour(self) -> None:
        colour = QColorDialog.getColor(initial=current_line_color)
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
        time_elapsed = (time() - start_testing) * 1000
        with open('report-functesting-latest.txt', 'a+') as f:
            f.write(f'{test_i}. Time elapsed: {time_elapsed:.3f} mc.\n')
    else:
        sys.exit(app.exec_())

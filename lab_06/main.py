import sys
from time import time

from typing import List, Tuple

from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsTextItem, QColorDialog, \
    QButtonGroup, QGraphicsRectItem
from PyQt5.QtGui import QWheelEvent, QMouseEvent, QPen, QColor, QFont

from dialogs import show_author, show_task, show_instruction, show_err_win, show_war_win
from class_point import Point
from input_checks import params_to_float
from paint_funcs import paint_alg, brezenhem_circle, brezenhem_ellipse
from point_funcs import del_lines_by_point

grid_lines: List[QGraphicsLineItem] = []
max_win_size: List[int] = [0, 0, 0]
point_list: List[Point] = []
point_scale: List[float] = []
coords_desc: List[QGraphicsTextItem] = []
scene_point_list: List[QGraphicsEllipseItem] = []
figures: List[List[Point]] = []
edges: List[List[QGraphicsLineItem]] = []
limit_figures: List[List[Point]] = []

scale: float = 1.0
prev_figure_points: int = 0
current_figure_points: int = 0

is_pressed: bool = False
dragging: bool = False

last_pos: QPoint = None
current_line_color: QColor = QColor(255, 0, 0)

seed_point: Point = None
scene_seed_point: QGraphicsEllipseItem = None


def delete_point_from_figures(del_point_id: int) -> None:
    k = del_point_id + 1
    for _ in range(len(figures)):
        if k - len(figures[_]) > 0:
            k -= len(figures[_])
        else:
            figures[_].pop(k - 1)


def delete_point_from_edges(del_point_id):
    if len(edges) > 1 and edges[del_point_id - 1]:
        for line in edges[del_point_id - 1]:
            if line in edges[del_point_id]:
                edges[del_point_id - 1].remove(line)
    if len(edges) > 1:
        if del_point_id + 1 < len(point_list):
            for line in edges[del_point_id + 1]:
                if line in edges[del_point_id]:
                    edges[del_point_id + 1].remove(line)
        elif figures and figures[0]:
            for line in edges[0]:
                if line in edges[del_point_id]:
                    edges[0].remove(line)


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("./lab_06/template.ui", self)  # временно в корне

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
        self.add_zt_button.clicked.connect(self.add_zt)
        self.add_figure_button.clicked.connect(self.add_figure)
        self.change_edge_button.clicked.connect(self.change_edge)
        self.change_color_button.clicked.connect(self.set_new_colour)
        self.close_figure_button.clicked.connect(self.close_figure)
        self.paint_figure_button.clicked.connect(self.paint_figures)

        self.figure_type_group = QButtonGroup()
        self.figure_type_group.addButton(self.set_circle_figure)
        self.figure_type_group.addButton(self.set_ellipse_figure)

        self.set_circle_figure.setChecked(True)
        self.set_circle_figure.toggled.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.page))
        self.set_ellipse_figure.toggled.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.page_2))
        self.stackedWidget.setCurrentWidget(self.page)

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
        elif event.button() == Qt.MiddleButton:
            self.add_zt_point_by_click(event)

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
        current_line_color = color
        objects = self.scene.items()
        for obj in objects:
            if obj not in grid_lines and not isinstance(obj, QGraphicsTextItem):
                obj.setPen(current_line_color)

    def change_edge(self, color: QColor):
        pass

    def clear_scene(self):
        global prev_figure_points, current_figure_points
        for item in self.scene.items():
            if item not in grid_lines:
                self.scene.removeItem(item)
        point_list.clear()
        point_scale.clear()
        coords_desc.clear()
        scene_point_list.clear()
        figures.clear()
        edges.clear()
        self.scroll_list.clear()
        prev_figure_points = 0
        current_figure_points = 0

    def add_point(self, point: Point = None) -> None:
        if not point:
            point = self.get_point_coords()
        if point is not None:
            self.draw_point(point)

    def get_point_coords(self) -> Point:
        x_txt = self.set_x.text()
        y_txt = self.set_y.text()
        params = params_to_float(x_txt, y_txt)
        if len(params) == 0:
            return
        x, y = params
        return Point(x, y)

    def add_point_by_click(self, event: QMouseEvent) -> None:
        pos = event.pos()
        scene_pos = self.graphicsView.mapToScene(pos)
        p_x, p_y = scene_pos.x(), scene_pos.y()
        self.draw_point(Point(p_x, -p_y))

    def draw_point(self, point: Point) -> None:
        global current_figure_points
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
            edges.append([])
            if len(point_list) > 1:
                self.draw_line(point_list[-2], point_list[-1])
            current_figure_points += 1
            scene_point_list.append(point)

    def draw_line(self, p1: Point, p2: Point) -> None:
        line = QGraphicsLineItem(p1.x, -p1.y, p2.x, -p2.y)
        line.setPen(current_line_color)
        line.setZValue(1)
        edges[-1].append(line)
        edges[-2].append(line)
        self.scene.addItem(line)

    def remove_point(self):
        point = self.get_point_coords()
        if point is None:
            return

        for i in range(len(point_list)):
            if point_list[i] == point:
                del_lines_by_point(edges, i)
                if edges[i]:
                    for line in edges[i]:
                        self.scene.removeItem(line)
                edges.pop(i)
                self.scene.removeItem(scene_point_list[i])
                self.scene.removeItem(coords_desc[i])
                coords_desc.pop(i)
                point_list.pop(i)
                scene_point_list.pop(i)
                point_scale.pop(i)
                self.update_scroll_list()
                break
        else:
            show_err_win("Введенной точки не существует.")
            return

        for i in range(len(figures)):
            for _ in range(len(figures[i])):
                if figures[i][_] == point:
                    figures[i].pop(_)
                    break

    def update_scroll_list(self) -> None:
        self.scroll_list.clear()
        for i in range(len(point_list)):
            self.scroll_list.addItem(f'{i + 1}.({round(point_list[i].x, 2)}; {round(point_list[i].y, 2)})')

    def close_figure(self):
        global prev_figure_points
        if len(point_list) < 2:
            show_err_win("Введено недостаточно точек для этого действия")
        else:
            self.draw_line(point_list[0], point_list[-1])
            figures.append(point_list[prev_figure_points:current_figure_points:])
            prev_figure_points = current_figure_points

    def del_point_by_click(self, event: QMouseEvent):
        pos = event.pos()
        scene_pos = self.graphicsView.mapToScene(pos)
        min_diff = 100 * (1 / scale)
        if min_diff < 1:
            min_diff = 1
        del_point_id = -1
        for i in range(len(point_list)):
            if abs(scene_pos.x() - point_list[i].x) + abs(scene_pos.y() + point_list[i].y) < min_diff:
                min_diff = abs(scene_pos.x() - point_list[i].x) + abs(scene_pos.y() + point_list[i].y)
                del_point_id = i
        if min_diff > 10 * (1 / scale):
            show_err_win("Кажется, вы пытаетесь удалить несуществующую точку.\nПопробуйте кликнуть ближе к точке.")
            return
        delete_point_from_figures(del_point_id)
        delete_point_from_edges(del_point_id)
        if edges[del_point_id]:
            for line in edges[del_point_id]:
                self.scene.removeItem(line)
        edges.pop(del_point_id)
        if del_point_id == len(point_list) - 1 and len(point_list) > 2:
            self.draw_line(point_list[del_point_id - 1], point_list[0])
        elif len(point_list) > 2:
            self.draw_line(point_list[del_point_id - 1], point_list[del_point_id + 1])
        self.scene.removeItem(scene_point_list[del_point_id])
        point_list.pop(del_point_id)
        scene_point_list.pop(del_point_id)
        point_scale.pop(del_point_id)
        self.scene.removeItem(coords_desc[del_point_id])
        coords_desc.pop(del_point_id)
        self.update_scroll_list()

    def set_new_colour(self) -> None:
        colour = QColorDialog.getColor(initial=current_line_color)
        if colour.isValid():
            self.change_color(QColor(colour))

    def paint_figures(self, func_testing=False):
        delay = False
        if self.set_delay_cb.isChecked():
            delay = True
        if len(figures) == 0:
            show_err_win("Ошибка. Фигура не замкнута")
            return
        if seed_point is None or scene_seed_point is None:
            show_err_win("Ошибка. Не задана затравочная точка.")
        start = time()
        paint_alg()
        end = time()
        if not delay:
            if func_testing:
                with open('report-functesting-latest.txt', 'a+') as f:
                    f.write(f"Время выполнения алгоритма в тесте {test_i}: {(end - start) * 1000:.2f} мс.\n")
            else:
                show_war_win(f"Время выполнения алгоритма: {(end - start) * 1000:.2f} мс.")

    def add_zt(self, point: Point = None) -> None:
        global seed_point
        if not point:
            seed_point = self.get_point_coords()
        else:
            seed_point = point
        if seed_point is not None:
            self.scene.removeItem(scene_seed_point)
            self.draw_zt_point()

    def draw_zt_point(self) -> None:
        global scene_seed_point
        scene_seed_point = QGraphicsEllipseItem(seed_point.x, -seed_point.y, 5, 5)
        scene_seed_point.setBrush(Qt.magenta)
        scene_seed_point.setZValue(1)
        self.scene.addItem(scene_seed_point)

    def add_figure(self):
        if self.set_circle_figure.isChecked():
            self.draw_circle()
        else:
            self.draw_ellipse()

    def draw_ellipse(self) -> None:
        coords = self.get_ellipse_params()
        if coords is None:
            return
        center, width, height = coords
        points = brezenhem_ellipse(center, width, height)
        limit_figures.append(points)
        for point in points:
            p = QGraphicsRectItem(point.x, -point.y, 1, 1)
            p.setPen(Qt.green)
            p.setZValue(1)
            self.scene.addItem(p)

    def get_ellipse_params(self) -> Tuple[Point, float, float]:
        xc_str = self.set_xc_ellipse.text()
        yc_str = self.set_yc_ellipse.text()
        width_str = self.set_ellipse_width.text()
        height_str = self.set_ellipse_height.text()
        params = params_to_float(xc_str, yc_str, width_str, height_str)
        if len(params) == 0:
            return
        xc, yc, width, height = params
        if width <= 0 or height <= 0:
            show_err_win("Значение высоты и ширины должно быть больше нуля!")
            return
        return Point(xc, yc), width, height

    def get_circle_params(self) -> Tuple[Point, float]:
        xc_str = self.set_xc_circle.text()
        yc_str = self.set_yc_circle.text()
        radius_str = self.set_r_circle.text()
        params = params_to_float(xc_str, yc_str, radius_str)
        if len(params) == 0:
            return
        xc, yc, radius = params
        if radius <= 0:
            show_err_win("Значение радиуса должно быть больше нуля!")
            return
        return Point(xc, yc), radius

    def draw_circle(self):
        coords = self.get_circle_params()
        if coords is None:
            return
        center, radius = coords
        points = brezenhem_circle(center, radius)
        limit_figures.append(points)
        for point in points:
            p = QGraphicsRectItem(point.x, -point.y, 1, 1)
            p.setPen(Qt.green)
            p.setZValue(1)
            self.scene.addItem(p)

    def add_zt_point_by_click(self, event: QMouseEvent) -> None:
        global seed_point
        pos = event.pos()
        scene_pos = self.graphicsView.mapToScene(pos)
        p_x, p_y = scene_pos.x(), scene_pos.y()
        if seed_point is not None and scene_seed_point is not None:
            self.scene.removeItem(scene_seed_point)
        seed_point = Point(p_x, -p_y)
        self.draw_zt_point()


if __name__ == '__main__':
    global test_i
    start_testing = time()
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()

    FUNC_TESTING = False
    if len(sys.argv) > 2:
        FUNC_TESTING = True
        test_i = int(sys.argv[1])
        num_points = int(sys.argv[2])
        for _ in range(num_points):
            window.add_point(Point(float(sys.argv[2 * _ + 3]), float(sys.argv[2 * _ + 4])))
        if sys.argv[-1] == 'true':
            window.set_delay_cb.setChecked(True)
        window.close_figure()
        window.paint_figures(func_testing=True)

    if FUNC_TESTING:
        screenshot = window.grab()
        screenshot.save(f'./results/test_{test_i}.png', 'png')
    else:
        sys.exit(app.exec_())

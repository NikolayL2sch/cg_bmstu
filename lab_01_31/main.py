import sys

from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QBrush
from PyQt5.QtWidgets import QMessageBox, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem

from triangle_methods import *

point_list = []
scene_point_list = []


def show_war_win(war):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText(war)
    msg.setWindowTitle("Предупреждение!")
    msg.exec_()


def show_err_win(err):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(err)
    msg.setWindowTitle("Ошибка!")
    msg.exec_()


def show_author():
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Об авторе")
    msg.setText(f"Лабораторная работа №1.\nРазработал Миленко Николай ИУ7-45Б")
    msg.exec_()


def show_task():
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Условие задачи")
    msg.setText(f"На плоскости дано множество точек.\n\nНайти такой треугольник с вершинами в этих точках, "
                f"у которого угол, образованный высотой и медианой, исходящими из одной вершины, минимален.\n\n"
                f"Вывести изображение в графическом режиме.\n\n31 Вариант.")
    msg.exec_()


def check_one_line():
    koeff_1 = (point_list[1].y - point_list[0].y) * (point_list[2].x - point_list[1].x)
    koeff_2 = (point_list[2].y - point_list[1].y) * (point_list[1].x - point_list[0].x)
    if abs(koeff_1 - koeff_2) < EPS:
        print(koeff_1, koeff_2)
        return True
    return False


def solve_task():
    coord_start, coord_perpend, coord_median = None, None, None
    min_angle = 180
    ans_vertex = []

    if not point_list or len(point_list) < 3:
        show_err_win("Недостаточно точек для решения задачи.\nДобавьте хотя бы 3 точки.")
        return
    if check_one_line():
        show_err_win("Невозможно построить треугольник.\nТочки лежат на одной прямой.")
        return

    for i in range(len(point_list) - 2):
        for j in range(i + 1, len(point_list) - 1):
            for k in range(j + 1, len(point_list)):
                pa = point_list[i]
                pb = point_list[j]
                pc = point_list[k]

                print(f"\n------ Points Triangle --------")
                print(f"pa = {pa.x, pa.y}\npb = {pb.x, pb.y}\npc = {pc.x, pc.y}")

                side_1 = side_len(pa, pb)
                side_2 = side_len(pa, pc)
                side_3 = side_len(pb, pc)
                print("----------Len Sides --------")
                print(side_1, side_2, side_3)

                if not is_triangle(side_1, side_2, side_3):
                    continue

                print("------Main vertex - pa:")
                pm_i, pp_i, angle_i = find_corner(pa, pb, pc)
                print("------ Main vertex - pb:")
                pm_j, pp_j, angle_j = find_corner(pb, pa, pc)
                print("------ Main vertex - pc:")
                pm_k, pp_k, angle_k = find_corner(pc, pb, pa)

                cur_min_angle = min(angle_i, angle_j, angle_k)
                if min_angle > cur_min_angle:
                    ans_vertex = [pa, pb, pc]
                    min_angle = cur_min_angle
                    if abs(angle_i - min_angle) < EPS:
                        coord_start = pa
                        coord_perpend = pp_i
                        coord_median = pm_i
                    if abs(angle_j - min_angle) < EPS:
                        coord_start = pb
                        coord_perpend = pp_j
                        coord_median = pm_j
                    if abs(angle_k - min_angle) < EPS:
                        coord_start = pc
                        coord_perpend = pp_k
                        coord_median = pm_k
    return ans_vertex, coord_start, coord_perpend, coord_median


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("./lab_01_31/template.ui", self)

        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)

        self.add_grid()
        self.greenBrush = QBrush(Qt.green)
        self.redBrush = QBrush(Qt.red)
        self.blueBrush = QBrush(Qt.blue)

        self.pen = QPen(Qt.red)

        self.add_point_button.clicked.connect(self.add_point)
        self.del_point_button.clicked.connect(self.del_point)
        self.solve_task_button.clicked.connect(self.draw_solution)

        self.about_author.triggered.connect(show_author)
        self.about_task.triggered.connect(show_task)

        self.graphicsView.mousePressEvent = self.on_graphicsview_click
        self.graphicsView.wheelEvent = self.wheel_event

        self.show()

    def add_grid(self):
        max_size = self.graphicsView.maximumSize()
        max_width = max_size.width()
        max_height = max_size.height()

        grid_interval = 30
        start_grid_width = - ((max_width // 2) + grid_interval - (max_width // 2) % grid_interval)
        start_grid_height = - ((max_height // 2) + grid_interval - (max_height // 2) % grid_interval)
        end_grid_width = (max_width // 2) - (max_width // 2) % grid_interval
        end_grid_height = (max_height // 2) - (max_width // 2) % grid_interval
        pen = QPen(Qt.darkGray)

        for x in range(start_grid_width, end_grid_width, grid_interval):
            line = QGraphicsLineItem(x, start_grid_height, x, end_grid_height)
            line.setPen(pen)
            self.scene.addItem(line)
        for y in range(start_grid_height, end_grid_height, grid_interval):
            line = QGraphicsLineItem(start_grid_width, y, end_grid_width, y)
            line.setPen(pen)
            self.scene.addItem(line)

        axis_x = QGraphicsLineItem(-300, 0, 300, 0)
        axis_y = QGraphicsLineItem(0, -300, 0, 300)
        pen.setColor(Qt.white)
        axis_x.setPen(pen)
        axis_y.setPen(pen)
        self.scene.addItem(axis_x)
        self.scene.addItem(axis_y)

    def add_point(self):
        x_txt = self.set_x_field.text()
        y_txt = self.set_y_field.text()
        if x_txt == '' or y_txt == '':
            show_err_win("Не введены координаты точки.")
        else:
            try:
                x, y = float(x_txt), float(y_txt)
                new_point = Point(x, y)
                for point in point_list:
                    if point == new_point:
                        show_war_win("Введенная точка уже существует.")
                        break
                else:
                    point_list.append(new_point)
                    self.scroll_list.addItem(f'{len(point_list)}.({round(x, 2)}; {round(y, 2)})')
                    self.draw_point(x, -y)
                    self.clear_fields()
            except:
                show_err_win("Введены некорректные символы.")

    def add_point_by_click(self, event):
        pos = event.pos()
        scene_pos = self.graphicsView.mapToScene(pos)
        p_x, p_y = scene_pos.x(), scene_pos.y()
        point = QGraphicsEllipseItem(p_x, p_y, 5, 5)
        point.setBrush(self.redBrush)
        self.scene.addItem(point)
        point_list.append(Point(p_x, -p_y))
        self.scroll_list.addItem(f'{len(point_list)}.({round(p_x, 2)}; {round(-p_y, 2)})')
        scene_point_list.append(point)

    def clear_fields(self):
        self.set_y_field.setText('')
        self.set_x_field.setText('')

    def del_point(self):
        x_txt = self.set_x_field.text()
        y_txt = self.set_y_field.text()
        if x_txt == '' or y_txt == '':
            show_err_win("Не введены координаты точки.")
        else:
            try:
                x, y = float(x_txt), float(y_txt)
                if abs(x) > 700 or abs(y) > 420:
                    show_err_win("Точка за пределами сетки")
                del_point = Point(x, y)
                for i in range(len(point_list)):
                    if point_list[i] == del_point:
                        self.scene.removeItem(scene_point_list[i])
                        point_list.pop(i)
                        scene_point_list.pop(i)
                        self.update_scroll_list()
                        break
                self.clear_fields()
            except:
                show_err_win("Введены некорректные символы.")

    def update_scroll_list(self):
        self.scroll_list.clear()
        for i in range(len(point_list)):
            self.scroll_list.addItem(f'{i}.({round(point_list[i].x, 2)}; {round(point_list[i].y, 2)})')

    def draw_point(self, p_x, p_y):
        point = QGraphicsEllipseItem(p_x, p_y, 5, 5)
        print(p_x, p_y)
        point.setBrush(self.redBrush)
        self.scene.addItem(point)
        scene_point_list.append(point)

    def del_point_by_click(self, event):
        pos = event.pos()
        scene_pos = self.graphicsView.mapToScene(pos)
        min_diff = 100
        del_point_id = -1
        for i in range(len(point_list)):
            if abs(scene_pos.x() - point_list[i].x) + abs(scene_pos.y() + point_list[i].y) < min_diff:
                min_diff = abs(scene_pos.x() - point_list[i].x) + abs(scene_pos.y() + point_list[i].y)
                del_point_id = i
        if min_diff > 10:
            show_err_win("Кажется, вы пытаетесь удалить несуществующую точку.\nПопробуйте кликнуть ближе к точке.")
        else:
            print(del_point_id)
            print(*scene_point_list)
            self.scene.removeItem(scene_point_list[del_point_id])
            point_list.pop(del_point_id)
            scene_point_list.pop(del_point_id)
            self.update_scroll_list()

    def on_graphicsview_click(self, event):
        if event.buttons() == Qt.LeftButton:
            self.add_point_by_click(event)
        elif event.buttons() == Qt.RightButton:
            self.del_point_by_click(event)

    def draw_solution(self):
        vertexes, coord_start, coord_perpend, coord_median = solve_task()

        side_1 = QGraphicsLineItem(vertexes[0].x, vertexes[0].y, vertexes[1].x, vertexes[1].y)
        side_2 = QGraphicsLineItem(vertexes[1].x, vertexes[1].y, vertexes[2].x, vertexes[2].y)
        side_3 = QGraphicsLineItem(vertexes[2].x, vertexes[2].y, vertexes[0].x, vertexes[0].y)
        perpend = QGraphicsLineItem(coord_start.x, coord_start.y, coord_perpend.x, coord_perpend.y)
        median = QGraphicsLineItem(coord_start.x, coord_start.y, coord_median.x, coord_median.y)

        pen_sides = QPen(Qt.magenta)
        pen_median = QPen(Qt.green)
        pen_perpend = QPen(Qt.yellow)

        pen_sides.setWidth(2)
        pen_median.setWidth(2)
        pen_perpend.setWidth(2)

        side_1.setPen(pen_sides)
        side_2.setPen(pen_sides)
        side_3.setPen(pen_sides)
        perpend.setPen(pen_perpend)
        median.setPen(pen_median)

        self.scene.addItem(side_1)
        self.scene.addItem(side_2)
        self.scene.addItem(side_3)
        self.scene.addItem(perpend)
        self.scene.addItem(median)

    def wheel_event(self, event):
        factor = 1.2

        if event.angleDelta().y() > 0:
            self.graphicsView.scale(factor, factor)
        else:
            self.graphicsView.scale(1.0 / factor, 1.0 / factor)

        current_scale = self.graphicsView.transform().m11()  # Получаем текущий масштаб по оси X (и Y)
        for point in scene_point_list:
            point.setTransformOriginPoint(point.boundingRect().center())
            point.setScale(1 / current_scale)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()

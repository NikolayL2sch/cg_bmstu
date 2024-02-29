import sys

from PyQt5 import QtWidgets, QtGui
from PyQt5 import uic
from PyQt5.QtCore import Qt, QPoint, QRectF
from PyQt5.QtGui import QPainterPath, QPen, QBrush, QPainter, QImage, QPolygonF, QPolygon, QColor
from PyQt5.QtWidgets import QMessageBox, QGraphicsScene, QGraphicsView, QGraphicsPathItem, QGraphicsEllipseItem, \
    QGraphicsLineItem

from class_point import *

point_list = []
scene_point_list = []


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

        self.about_author.triggered.connect(self.show_author)
        self.about_task.triggered.connect(self.show_task)

        self.graphicsView.mousePressEvent = self.on_graphicsview_click

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
            self.show_err_win("Не введены координаты точки.")
        else:
            try:
                x, y = float(x_txt), float(y_txt)
                new_point = Point(x, y)
                for point in point_list:
                    if point == new_point:
                        self.show_war_win("Введенная точка уже существует.")
                        break
                else:
                    if abs(x) > 700 or abs(y) > 420:
                        self.show_err_win("Точка за пределами сетки")
                    point_list.append(new_point)
                    self.scroll_list.addItem(f'{len(point_list)}.({round(x, 2)}; {round(y, 2)})')
                    self.draw_point(x, y)
                    self.clear_fields()
            except:
                self.show_err_win("Введены некорректные символы.")

    def add_point_by_click(self, event):
        pos = event.pos()
        scene_pos = self.graphicsView.mapToScene(pos)
        p_x, p_y = scene_pos.x(), scene_pos.y()
        point = QGraphicsEllipseItem(p_x, p_y, 5, 5)
        point.setBrush(self.redBrush)
        self.scene.addItem(point)
        point_list.append(Point(p_x, p_y))
        self.scroll_list.addItem(f'{len(point_list)}.({round(p_x, 2)}; {round(p_y, 2)})')
        scene_point_list.append(point)

    def show_err_win(self, err):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(err)
        msg.setWindowTitle("Ошибка!")
        msg.exec_()

    def show_war_win(self, war):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(war)
        msg.setWindowTitle("Предупреждение!")
        msg.exec_()

    def clear_fields(self):
        self.set_y_field.setText('')
        self.set_x_field.setText('')

    def show_author(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Об авторе")
        msg.setText(f"Лабораторная работа №1.\nРазработал Миленко Николай ИУ7-45Б")
        msg.exec_()

    def del_point(self):
        x_txt = self.set_x_field.text()
        y_txt = self.set_y_field.text()
        if x_txt == '' or y_txt == '':
            self.show_err_win("Не введены координаты точки.")
        else:
            try:
                x, y = float(x_txt), float(y_txt)
                if abs(x) > 700 or abs(y) > 420:
                    self.show_err_win("Точка за пределами сетки")
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
                self.show_err_win("Введены некорректные символы.")

    def update_scroll_list(self):
        self.scroll_list.clear()
        for i in range(len(point_list)):
            self.scroll_list.addItem(f'{i}.({round(point_list[i].x, 2)}; {round(point_list[i].y, 2)})')

    def show_task(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Условие задачи")
        msg.setText(f"На плоскости дано множество точек.\n\nНайти такой треугольник с вершинами в этих точках, "
                    f"у которого угол, образованный высотой и медианой, исходящими из одной вершины, минимален.\n\n"
                    f"Вывести изображение в графическом режиме.\n\n31 Вариант.")
        msg.exec_()

    def draw_point(self, p_x, p_y):
        point = QGraphicsEllipseItem(p_x, p_y, 5, 5)
        point.setBrush(self.redBrush)
        self.scene.addItem(point)
        scene_point_list.append(point)

    def del_point_by_click(self, event):
        pos = event.pos()
        scene_pos = self.graphicsView.mapToScene(pos)
        min_diff = 100
        del_point_id = -1
        for i in range(len(point_list)):
            if abs(scene_pos.x() - point_list[i].x) + abs(scene_pos.y() - point_list[i].y) < min_diff:
                min_diff = abs(scene_pos.x() - point_list[i].x) + abs(scene_pos.y() - point_list[i].y)
                del_point_id = i
        if min_diff > 10:
            self.show_err_win("Кажется, вы пытаетесь удалить несуществующую точку.\nПопробуйте кликнуть ближе к точке.")
        else:
            self.scene.removeItem(scene_point_list[del_point_id])
            point_list.pop(del_point_id)
            scene_point_list.pop(del_point_id)
            self.update_scroll_list()

    def on_graphicsview_click(self, event):
        if event.buttons() == Qt.LeftButton:
            self.add_point_by_click(event)
        elif event.buttons() == Qt.RightButton:
            self.del_point_by_click(event)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()

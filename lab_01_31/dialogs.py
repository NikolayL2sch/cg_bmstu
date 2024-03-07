from PyQt5.QtWidgets import QMessageBox


def show_war_win(war: str) -> None:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText(war)
    msg.setWindowTitle("Предупреждение!")
    msg.exec_()


def show_err_win(err: str) -> None:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(err)
    msg.setWindowTitle("Ошибка!")
    msg.exec_()


def show_author():
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Об авторе")
    msg.setText("Лабораторная работа №1.\nРазработал Миленко Николай ИУ7-45Б")
    msg.exec_()


def show_task():
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Условие задачи")
    msg.setText("На плоскости дано множество точек.\n\nНайти такой треугольник с вершинами в этих точках, "
                "у которого угол, образованный высотой и медианой, исходящими из одной вершины, минимален.\n\n"
                "Вывести изображение в графическом режиме.\n\n31 Вариант.")
    msg.exec_()


def show_instruction():
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Возможности программы")
    msg.setText("Добавление точек.\nПо введенным координатам/по клику ЛЕВОЙ кнокой мыши на график.\n\nУдаление "
                "точек.\nПо клику ПРАВОЙ кнопкой мыши на графике достаточно близко к удаляемой "
                "точке.\n\nМасштабирование окна при изменении его размеров происходит "
                "автоматически.\nРеализовано масштабирование графика с помощью колеса мыши. Шаг сетки меняется "
                "автоматически и указан в левом нижнем углу экрана.")
    msg.exec_()

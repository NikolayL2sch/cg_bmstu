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
    msg.setText("Лабораторная работа №6.\nРазработал Миленко Николай ИУ7-45Б")
    msg.exec_()


def show_task():
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Условие задачи")
    msg.setText('Программа обеспечивает ввод произвольной многоугольной области, содержащей произвольное количество '
                'отверстий, дальнейшее заполнение сплошных областей с указанной затравочной точкой и задержкой (или '
                'ее отсутствием).')
    msg.exec_()


def show_instruction():
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Возможности программы")
    msg.setText("Смена цвета закраски.\nВыбор одного из предложенных цветов меняет цвет закраски для будущих "
                "фигур.\n\nПостроение фигуры по координатам (точкам). Точки могут вводиться кликом левой кнопкой мыши "
                "по экрану. Удаление точек происходит кликом правой кнопкой мыши или вручную вводом координат.\n\n"
                "Рисование кривых осуществляется посредством зажатой правой мыши, кривая повторит траекторию мыши"
                "на экране.\n\n"
                "Ввод затравочной точки осуществляется кликом средней кнопкой мыши в нужной точке. Предусмотрены """
                "ограничения области закраски эллипсом или окружностью.")
    msg.exec_()

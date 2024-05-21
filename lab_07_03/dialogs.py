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
    msg.setText("Лабораторная работа №7.\nРазработал Миленко Николай ИУ7-45Б")
    msg.exec_()


def show_task():
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Условие задачи")
    msg.setText(
        'Программа реализует алгоритм разбиения отрезка средней точкой.\n')
    msg.exec_()


def show_instruction():
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Возможности программы")
    msg.setText("Смена цвета регулярного отсекателя/отрезков.\nВыбор одного из предложенных цветов меняет цвет "
                "закраски для всех БУДУЩИХ графических объектов этого типа."
                "фигур.\n\nВвод регулярного отсекателя (прямоугольника) осуществляется зажатием ЛКМ + движением мыши "
                "в предпочитаемом направлении. Предварительно для ввода регулярного отсекателя необходимо нажать на "
                "кнопку с надписью 'Добавить регулярный отсекатель'. \nПосле ввода отсекателя необходимо нажать на "
                "кнопку с надписью 'Закончить добавление отсекателя'."
                "\n\nВвод отрезков осуществляется путем добавления концов отрезка по клику левой кнопкой мыши в "
                "выбранном пользователем месте.\n Обратите внимание, что отрезок является введенным, если заданы обе"
                "точки - концы отрезка.")
    msg.exec_()

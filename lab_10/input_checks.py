from dialogs import show_err_win
from typing import List


def params_to_int(*args: List[str]) -> List[int]:
    int_args = []
    if '' in args:
        show_err_win("Не введены все параметры для совершения этого действия")
        return int_args
    try:
        int_args = [int(arg) for arg in args]
    except ValueError:
        show_err_win("Введены некорректные символы")
    return int_args

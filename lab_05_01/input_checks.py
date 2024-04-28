from dialogs import show_err_win
from typing import List


def params_to_float(*args: List[str]) -> List[float]:
    float_args = []
    if '' in args:
        show_err_win("Не введены все параметры для совершения этого действия")
        return float_args
    try:
        float_args = [float(arg) for arg in args]
    except ValueError:
        show_err_win("Введены некорректные символы")
    return float_args

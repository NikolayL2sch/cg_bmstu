from dialogs import show_err_win
from typing import List, Union, Tuple


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


def validate_circle_spektre_params(cnt, ind, params) -> Union[None, Tuple[Union[float, int]]]:
    if cnt != 1:
        show_err_win("Должно быть задано ровно 3 параметра.")
        return
    if ind == -1:
        show_err_win("Должно быть задано ровно 3 параметра.")
        return
    if ind == 0:
        float_params = params_to_float(params[1], params[2], params[3])
        if len(float_params) == 0:
            show_err_win("Введены некорректные символы")
            return
        r_end, circle_cnt, step = float_params
        r_start = r_end - step * circle_cnt
    elif ind == 1:
        float_params = params_to_float(params[0], params[2], params[3])
        if len(float_params) == 0:
            show_err_win("Введены некорректные символы")
            return
        r_start, circle_cnt, step = float_params
        r_end = r_start + step * circle_cnt
    elif ind == 2:
        float_params = params_to_float(params[0], params[1], params[3])
        if len(float_params) == 0:
            show_err_win("Введены некорректные символы")
            return
        r_start, r_end, step = float_params
        circle_cnt = (r_end - r_start) / step
    else:
        float_params = params_to_float(params[0], params[1], params[2])
        if len(float_params) == 0:
            show_err_win("Введены некорректные символы")
            return
        r_start, r_end, circle_cnt = float_params
        step = (r_end - r_start) / circle_cnt

    if r_start <= 0 or r_end <= r_start or r_end <= 0 or abs(int(circle_cnt) - circle_cnt) > 1e-13:
        show_err_win("Введенные значения некорректны!")
        return

    return r_start, r_end, int(circle_cnt), step

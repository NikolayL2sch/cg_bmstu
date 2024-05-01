from typing import List

from PyQt5.QtWidgets import QGraphicsLineItem


def del_lines_by_point(edges: List[QGraphicsLineItem], ind: int) -> None:
    if len(edges) > 1 and edges[ind - 1]:
        for line in edges[ind - 1]:
            if line in edges[ind]:
                edges[ind - 1].remove(line)
    if len(edges) > 1 and edges[ind + 1]:
        for line in edges[ind + 1]:
            if line in edges[ind]:
                edges[ind + 1].remove(line)

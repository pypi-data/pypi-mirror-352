# -*- coding: utf-8 -*-
from typing import List
from .bill import Bill
from ..canvas.canvas_base import CanvasBase
from .qr_code_text import QRCodeText
from qrcodegen import QrCode as QrCodeGen
import math


class QRCode:
    SIZE = 46

    def __init__(self, bill: Bill) -> None:
        self._embedded_text = QRCodeText.create(bill)

    def draw(self, canvas: CanvasBase, offset_X: float, offset_Y: float):
        BAR_WIDTH = 7 / 6.0
        BAR_LENGTH = 35 / 9.0
        qr_code = QrCodeGen.encode_text(self._embedded_text, QrCodeGen.Ecc.MEDIUM)
        modules = _copy_modules(qr_code)
        _clear_swiss_cross_area(modules)
        canvas.set_transformation(offset_X, offset_Y, 0, QRCode.SIZE / len(modules) / 25.4 * 72, QRCode.SIZE / len(modules) / 25.4 * 72)
        canvas.start_path()
        _draw_modules_path(canvas, modules)
        canvas.fill_path(0, False)
        canvas.set_transformation(offset_X, offset_Y, 0, 1, 1)
        # Swiss cross
        canvas.start_path()
        canvas.add_rectangle(20, 20, 6, 6)
        canvas.fill_path(0, False)
        canvas.start_path()
        canvas.move_to(23 - BAR_WIDTH / 2, 23 - BAR_LENGTH / 2)
        canvas.line_to(23 + BAR_WIDTH / 2, 23 - BAR_LENGTH / 2)
        canvas.line_to(23 + BAR_WIDTH / 2, 23 - BAR_WIDTH / 2)
        canvas.line_to(23 + BAR_LENGTH / 2, 23 - BAR_WIDTH / 2)
        canvas.line_to(23 + BAR_LENGTH / 2, 23 + BAR_WIDTH / 2)
        canvas.line_to(23 + BAR_WIDTH / 2, 23 + BAR_WIDTH / 2)
        canvas.line_to(23 + BAR_WIDTH / 2, 23 + BAR_LENGTH / 2)
        canvas.line_to(23 - BAR_WIDTH / 2, 23 + BAR_LENGTH / 2)
        canvas.line_to(23 - BAR_WIDTH / 2, 23 + BAR_WIDTH / 2)
        canvas.line_to(23 - BAR_LENGTH / 2, 23 + BAR_WIDTH / 2)
        canvas.line_to(23 - BAR_LENGTH / 2, 23 - BAR_WIDTH / 2)
        canvas.line_to(23 - BAR_WIDTH / 2, 23 - BAR_WIDTH / 2)
        canvas.fill_path(0xffffff, False)


def _copy_modules(qr_code: QrCodeGen) -> List[List[bool]]:
    size = qr_code.get_size()
    modules: List[List[bool]] = []
    for y in range(size):
        row = []
        for x in range(size):
            row.append(qr_code.get_module(x, y))
        modules.append(row)
    return modules


def _clear_rectangle(modules: List[List[bool]], x: int, y: int, width: int, height: int) -> None:
    for iy in range(y, y + height):
        for ix in range(x, x + width):
            modules[iy][ix] = False


def _clear_swiss_cross_area(modules: List[List[bool]]):
    size = len(modules)
    start = math.floor((46 - 6.5) / 2 * size / 46)
    _clear_rectangle(modules, start, start, size - 2 * start, size - 2 * start)


def _draw_largest_rectangle(canvas: CanvasBase, modules: List[List[bool]], x: int, y: int):
    UNIT = 25.4 / 72
    size = len(modules)

    best_W = 1
    best_H = 1
    max_area = 1
    x_limit = size
    iy = y
    while iy < size and modules[iy][x] is True:
        w = 0
        while x + w < x_limit and modules[iy][x + w] is True:
            w += 1
        area = w * (iy - y + 1)
        if area > max_area:
            max_area = area
            best_W = w
            best_H = iy - y + 1
        x_limit = x + w
        iy += 1
    canvas.add_rectangle(x * UNIT, (size - y - best_H) * UNIT, best_W * UNIT, best_H * UNIT)
    _clear_rectangle(modules, x, y, best_W, best_H)


def _draw_modules_path(canvas: CanvasBase, modules: List[List[bool]]):
    # Simple algorithm to reduce the number of drawn rectangles
    size = len(modules)
    for y in range(size):
        for x in range(size):
            if modules[y][x] is True:
                _draw_largest_rectangle(canvas, modules, x, y)

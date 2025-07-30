# -*- coding: utf-8 -*-
from ..validator.helpers import ValidationResult
from ..validator.validator import Validator
from ..canvas.canvas_base import CanvasBase
from ..canvas.svg_canvas import SVGCanvas
from .bill import Bill
from .bill_format import BillFormat
from .bill_layout import BillLayout
from .enums import GraphicsFormat, OutputSize
from .qr_code import QRCode


class QRBill:
    A4_PORTRAIT_WIDTH = 210.0
    A4_PORTRAIT_HEIGHT = 297.0
    QR_BILL_WIDTH = 210.0
    QR_BILL_HEIGHT = 105.0
    QR_BILL_WITH_HORI_LINE_WIDTH = 210.0
    QR_BILL_WITH_HORI_LINE_HEIGHT = 107.0
    QR_CODE_WIDTH = 46.0
    QR_CODE_HEIGHT = 46.0

    def __init__(self) -> None:
        pass

    @staticmethod
    def validate(bill: Bill) -> ValidationResult:
        return Validator.validate(bill)

    @staticmethod
    def validate_and_generate(bill: Bill, canvas: CanvasBase):
        result = Validator.validate(bill)
        cleaned_bill = result.cleaned_bill
        if result.has_errors:
            print(result.get_description())
            return
        if bill.format.output_size == OutputSize.QR_CODE_ONLY:
            qr_code = QRCode(cleaned_bill)
            qr_code.draw(canvas, 0, 0)
        else:
            layout = BillLayout(cleaned_bill, canvas)
            layout.draw()

    @staticmethod
    def generate(bill: Bill) -> CanvasBase:
        canvas = QRBill.create_canvas(bill.format)
        QRBill.validate_and_generate(bill, canvas)
        return canvas

    @staticmethod
    def create_canvas(format: BillFormat) -> CanvasBase:
        drawing_width = 0.0
        drawing_height = 0.0

        # define page size
        if format.output_size == OutputSize.QR_BILL_ONLY:
            drawing_width = QRBill.QR_BILL_WIDTH
            drawing_height = QRBill.QR_BILL_HEIGHT
        elif format.output_size == OutputSize.QR_BILL_EXTRA_SPACE:
            drawing_width = QRBill.QR_BILL_WITH_HORI_LINE_WIDTH
            drawing_height = QRBill.QR_BILL_WITH_HORI_LINE_HEIGHT
        elif format.output_size == OutputSize.QR_CODE_ONLY:
            drawing_width = QRBill.QR_CODE_WIDTH
            drawing_height = QRBill.QR_CODE_HEIGHT
        else:
            drawing_width = QRBill.A4_PORTRAIT_WIDTH
            drawing_height = QRBill.A4_PORTRAIT_HEIGHT

        if format.graphics_format == GraphicsFormat.SVG:
            canvas = SVGCanvas(drawing_width, drawing_height, format.font_family)
        elif format.graphics_format == GraphicsFormat.PDF:
            # canvas = PDFCanvas(drawing_width, drawing_height)
            raise NotImplementedError
        elif format.graphics_format == GraphicsFormat.PNG:
            # canvas = PNGCanvas(drawing_width, drawing_height, format.resolution, format.font_family)
            raise NotImplementedError
        else:
            raise Exception("Invalid graphics format specified")
        return canvas

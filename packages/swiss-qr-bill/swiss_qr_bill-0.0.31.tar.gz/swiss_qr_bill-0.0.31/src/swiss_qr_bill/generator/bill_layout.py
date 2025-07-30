# -*- coding: utf-8 -*-
from typing import List

from affine import Affine
from stdnum import iban
from stdnum.ch import esr

from ..canvas.canvas_base import CanvasBase, LineStyle
from .address import Address
from .bill import Bill
from .enums import AddressType, OutputSize, SeparatorType, VerticalBorderType
from .multi_lingual_text import MultiLingualText as MLT
from .qr_code import QRCode

PT_TO_MM = 25.4 / 72
MM_TO_PT = 72 / 25.4
FONT_SIZE_TITLE = 11  # pt
SLIP_WIDTH = 210.0  # mm
SLIP_HEIGHT = 105.0  # mm
MARGIN = 5.0  # mm
RECEIPT_WIDTH = 62.0  # mm
RECEIPT_TEXT_WIDTH = 52.0  # mm
PAYMENT_PART_WIDTH = 148.0  # mm
PP_AMOUNT_SECTION_WIDTH = 46.0  # mm
PP_INFO_SECTION_WIDTH = 87.0  # mm
AMOUNT_SECTION_TOP = 37.0  # mm (from bottom)
BOX_TOP_PADDING = 2.0 * PT_TO_MM  # mm
DEBTOR_BOX_WIDTH_PP = 65.0  # mm
DEBTOR_BOX_HEIGHT_PP = 25.0  # mm
DEBTOR_BOX_WIDTH_RC = 52.0  # mm
DEBTOR_BOX_HEIGHT_RC = 20.0  # mm
PP_LABEL_PREF_FONT_SIZE = 8  # pt
PP_TEXT_PREF_FONT_SIZE = 10  # pt
PP_TEXT_MIN_FONT_SIZE = 8  # pt
RC_LABEL_PREF_FONT_SIZE = 6  # pt
RC_TEXT_PREF_FONT_SIZE = 8  # pt


class BillLayout:
    def __init__(self, bill: Bill, graphics: CanvasBase) -> None:
        MLT.set_language(bill.format.language)
        self._bill = bill
        self._qr_code = QRCode(bill)
        self._graphics = graphics
        self._additional_left_margin = min(max(bill.format.margin_left, 5.0), 12.0) - MARGIN
        self._additional_right_margin = min(max(bill.format.margin_right, 5.0), 12.0) - MARGIN
        # Text info
        self._account: str = None
        self._account_payable_to: str = None
        self._reference: str = None
        self._info: str = None
        self._additional_info: str = None
        self._payable_by: str = None
        self._amount: float = None
        self._label_font_size = PP_LABEL_PREF_FONT_SIZE
        self._text_font_size = PP_TEXT_PREF_FONT_SIZE
        self._label_ascender = 0.0
        self._text_ascender = 0.0
        self._y_pos = 0.0
        self._line_spacing = 0.0
        self._extra_spacing = 0.0
        #
        self._account_payable_to_lines: List[str] = []
        self._additional_info_lines: List[str] = []
        self._payable_by_lines: List[str] = []

    def draw(self):
        self.prepare_text()

        # Payment part
        is_too_tight = False
        while True:
            self.break_lines(PP_INFO_SECTION_WIDTH - self._additional_right_margin)
            is_too_tight = self.compute_payment_part_spacing()
            if not is_too_tight or self._text_font_size == PP_TEXT_MIN_FONT_SIZE:
                break
            self._label_font_size -= 1
            self._text_font_size -= 1
        self.draw_payment_part()

        # Receipt
        self._label_font_size = RC_LABEL_PREF_FONT_SIZE
        self._text_font_size = RC_TEXT_PREF_FONT_SIZE
        receipt_text_width_adapted = RECEIPT_TEXT_WIDTH - self._additional_left_margin
        self.break_lines(receipt_text_width_adapted)
        is_too_tight = self.compute_receipt_spacing()
        if is_too_tight:
            self.prepare_reduced_receipt_text(False)
            self.break_lines(receipt_text_width_adapted)
            is_too_tight = self.compute_receipt_spacing()
        if is_too_tight:
            self.prepare_reduced_receipt_text(True)
            self.break_lines(receipt_text_width_adapted)
            self.compute_receipt_spacing()

        self.draw_receipt()

        # border
        self.draw_border()

    def draw_payment_part(self):
        QR_CODE_BOTTOM = 42.0  # mm

        # title section
        self._graphics.set_transformation(RECEIPT_WIDTH + MARGIN, 0, 0, 1, 1)
        self._y_pos = SLIP_HEIGHT - MARGIN - self._graphics.get_ascender(FONT_SIZE_TITLE)
        self._graphics.put_text(MLT.get_text(MLT.Keys.KEY_PAYMENT_PART), 0, self._y_pos, FONT_SIZE_TITLE, True)

        # Swiss QR code section
        self._qr_code.draw(self._graphics, RECEIPT_WIDTH + MARGIN, QR_CODE_BOTTOM)

        # amount section
        self.draw_payment_part_amount_section()

        # information section
        self.draw_payment_part_information_section()

        # further information section
        self.draw_further_information_section()

    def draw_payment_part_amount_section(self):
        CURRENCY_WIDTH_PP = 15.0  # mm
        AMOUNT_BOX_WIDTH_PP = 40.0  # mm
        AMOUNT_BOX_HEIGHT_PP = 15.0  # mm

        self._graphics.set_transformation(RECEIPT_WIDTH + MARGIN, 0, 0, 1, 1)

        # currency
        y = AMOUNT_SECTION_TOP - self._label_ascender
        label = MLT.get_text(MLT.Keys.KEY_CURRENCY)
        self._graphics.put_text(label, 0, y, self._label_font_size, True)

        y -= (self._text_font_size + 3) * PT_TO_MM
        self._graphics.put_text(self._bill.currency, 0, y, self._text_font_size, False)

        # amount
        y = AMOUNT_SECTION_TOP - self._label_ascender
        label = MLT.get_text(MLT.Keys.KEY_AMOUNT)
        self._graphics.put_text(label, CURRENCY_WIDTH_PP, y, self._label_font_size, True)

        y -= (self._text_font_size + 3) * PT_TO_MM
        if self._amount is not None:
            self._graphics.put_text(self._amount, CURRENCY_WIDTH_PP, y, self._text_font_size, False)
        else:
            y -= -self._text_ascender + AMOUNT_BOX_HEIGHT_PP
            self.draw_corners(PP_AMOUNT_SECTION_WIDTH + MARGIN - AMOUNT_BOX_WIDTH_PP, y, AMOUNT_BOX_WIDTH_PP, AMOUNT_BOX_HEIGHT_PP)

    def draw_payment_part_information_section(self):
        self._graphics.set_transformation(SLIP_WIDTH - PP_INFO_SECTION_WIDTH - MARGIN, 0, 0, 1, 1)
        self._y_pos = SLIP_HEIGHT - MARGIN - self._label_ascender

        # account and creditor
        self.draw_label_and_text_lines(MLT.Keys.KEY_ACCOUNT_PAYABLE_TO, self._account_payable_to_lines)

        # reference
        if self._reference is not None:
            self.draw_label_and_text(MLT.Keys.KEY_REFERENCE, self._reference)

        # additional information
        if self._additional_info is not None:
            self.draw_label_and_text_lines(MLT.Keys.KEY_ADDITIONAL_INFO, self._additional_info_lines)

        # payable by
        if self._payable_by is not None:
            self.draw_label_and_text_lines(MLT.Keys.KEY_PAYABLE_BY, self._payable_by_lines)
        else:
            self.draw_label(MLT.Keys.KEY_PAYABLE_BY_NAME_ADDR)
            self._y_pos -= -self._text_ascender + BOX_TOP_PADDING
            self._y_pos -= DEBTOR_BOX_HEIGHT_PP
            self.draw_corners(0, self._y_pos, DEBTOR_BOX_WIDTH_PP, DEBTOR_BOX_HEIGHT_PP)

    def draw_further_information_section(self):
        FONT_SIZE = 7
        LINE_SPACING = 8
        FURTHER_INFORMATION_SECTION_TOP = 15.0  # mm

        if self._bill.alternative_schemes is None or len(self._bill.alternative_schemes) == 0:
            return

        self._graphics.set_transformation(RECEIPT_WIDTH + MARGIN, 0, 0, 1, 1)
        y = FURTHER_INFORMATION_SECTION_TOP - self._graphics.get_ascender(FONT_SIZE)
        max_width = PAYMENT_PART_WIDTH - 2 * MARGIN - self._additional_right_margin

        for scheme in self._bill.alternative_schemes:
            bold_text = f"{scheme.name}: "
            bold_text_width = self._graphics.get_text_width(bold_text, FONT_SIZE, True)
            self._graphics.put_text(bold_text, 0, y, FONT_SIZE, True)
            normal_text = self.truncate_text(scheme.instruction, max_width - bold_text_width, FONT_SIZE)
            self._graphics.put_text(normal_text, bold_text_width, y, FONT_SIZE, False)
            y -= LINE_SPACING * PT_TO_MM

    def draw_receipt(self):
        # "Receipt" title
        self._graphics.set_transformation(MARGIN + self._additional_left_margin, 0, 0, 1, 1)
        self._y_pos = SLIP_HEIGHT - MARGIN - self._graphics.get_ascender(FONT_SIZE_TITLE)
        self._graphics.put_text(MLT.get_text(MLT.Keys.KEY_RECEIPT), 0, self._y_pos, FONT_SIZE_TITLE, True)

        # information section
        self.draw_receipt_information_section()

        # amount section
        self.draw_receipt_amount_section()

        # acceptance point
        self.draw_receipt_acceptance_point_section()

    def draw_receipt_information_section(self):
        TITLE_HEIGHT = 7.0  # mm

        # payable to
        self._y_pos = SLIP_HEIGHT - MARGIN - TITLE_HEIGHT - self._label_ascender
        self.draw_label_and_text_lines(MLT.Keys.KEY_ACCOUNT_PAYABLE_TO, self._account_payable_to_lines)

        # reference
        if self._reference is not None:
            self.draw_label_and_text(MLT.Keys.KEY_REFERENCE, self._reference)

        # payable by
        if self._payable_by is not None:
            self.draw_label_and_text_lines(MLT.Keys.KEY_PAYABLE_BY, self._payable_by_lines)
        else:
            self.draw_label(MLT.Keys.KEY_PAYABLE_BY_NAME_ADDR)
            self._y_pos -= -self._text_ascender + BOX_TOP_PADDING
            self._y_pos -= DEBTOR_BOX_HEIGHT_RC
            self.draw_corners(0, self._y_pos, DEBTOR_BOX_WIDTH_RC - self._additional_left_margin, DEBTOR_BOX_HEIGHT_RC)

    def draw_receipt_amount_section(self):
        CURRENCY_WIDTH_RC = 12.0  # mm
        AMOUNT_BOX_WIDTH_RC = 30.0  # mm
        AMOUNT_BOX_HEIGHT_RC = 10.0  # mm

        # currency
        y = AMOUNT_SECTION_TOP - self._label_ascender
        label = MLT.get_text(MLT.Keys.KEY_CURRENCY)
        self._graphics.put_text(label, 0, y, self._label_font_size, True)

        y -= (self._text_font_size + 3) * PT_TO_MM
        self._graphics.put_text(self._bill.currency, 0, y, self._text_font_size, False)

        # amount
        y = AMOUNT_SECTION_TOP - self._label_ascender
        label = MLT.get_text(MLT.Keys.KEY_AMOUNT)
        self._graphics.put_text(label, CURRENCY_WIDTH_RC, y, self._label_font_size, True)

        if self._amount is not None:
            y -= (self._text_font_size + 3) * PT_TO_MM
            self._graphics.put_text(self._amount, CURRENCY_WIDTH_RC, y, self._text_font_size, False)
        else:
            self.draw_corners(RECEIPT_TEXT_WIDTH - AMOUNT_BOX_WIDTH_RC, AMOUNT_SECTION_TOP - AMOUNT_BOX_HEIGHT_RC, AMOUNT_BOX_WIDTH_RC - self._additional_left_margin, AMOUNT_BOX_HEIGHT_RC)

    def draw_receipt_acceptance_point_section(self):
        ACCEPTANCE_POINT_SECTION_TOP = 23.0  # mm (from bottom)
        label = MLT.get_text(MLT.Keys.KEY_ACCEPTANCE_POINT)
        y = ACCEPTANCE_POINT_SECTION_TOP - self._label_ascender
        w = self._graphics.get_text_width(label, self._label_font_size, True)
        self._graphics.put_text(label, RECEIPT_TEXT_WIDTH - self._additional_left_margin - w, y, self._label_font_size, True)

    def compute_payment_part_spacing(self) -> bool:
        PP_INFO_SECTION_MAX_HEIGHT = 85.0  # mm

        num_text_lines = 0
        num_extra_lines = 0  # number of lines between text blocks
        fixed_height = 0.0

        num_text_lines += 1 + len(self._account_payable_to_lines)
        if self._reference is not None:
            num_extra_lines += 1
            num_text_lines += 2
        if self._additional_info is not None:
            num_extra_lines += 1
            num_text_lines += 1 + len(self._additional_info_lines)
        num_extra_lines += 1
        if self._payable_by is not None:
            num_text_lines += 1 + len(self._payable_by_lines)
        else:
            num_extra_lines += 1
            fixed_height += DEBTOR_BOX_HEIGHT_PP

        # extra spacing line if there are alternative schemes
        if self._bill.alternative_schemes is not None and len(self._bill.alternative_schemes) > 0:
            num_extra_lines += 1

        return self.compute_spacing(PP_INFO_SECTION_MAX_HEIGHT, fixed_height, num_text_lines, num_extra_lines)

    def compute_receipt_spacing(self):
        RECEIPT_MAX_HEIGHT = 56.0  # mm

        # numExtraLines: the number of lines between text blocks
        numTextLines = 0
        numExtraLines = 0
        fixedHeight = 0.0

        numTextLines += 1 + len(self._account_payable_to_lines)
        if self._reference is not None:
            numExtraLines += 1
            numTextLines += 2

        numExtraLines += 1
        if self._payable_by is not None:
            numTextLines += 1 + len(self._payable_by_lines)
        else:
            numTextLines += 1
            fixedHeight += DEBTOR_BOX_HEIGHT_RC

        numExtraLines += 1
        return self.compute_spacing(RECEIPT_MAX_HEIGHT, fixedHeight, numTextLines, numExtraLines)

    def compute_spacing(self, max_height: float, fixed_height: float, num_text_lines: int, num_extra_lines: int) -> bool:
        self._line_spacing = (self._text_font_size + 1) * PT_TO_MM
        self._extra_spacing = (max_height - fixed_height - (num_text_lines * self._line_spacing)) / num_extra_lines
        self._extra_spacing = min(max(self._extra_spacing, 0), self._line_spacing)

        self._label_ascender = self._graphics.get_ascender(self._label_font_size)
        self._text_ascender = self._graphics.get_ascender(self._text_font_size)

        return (self._extra_spacing / self._line_spacing) < 0.8

    def draw_border(self):
        separator_type = self._bill.format.separator_type
        vertical_border_type = self._bill.format.vertical_border_type
        output_size = self._bill.format.output_size

        if separator_type == SeparatorType.NONE:
            return

        has_scissors = separator_type in [SeparatorType.SOLID_LINE_WITH_SCISSORS, SeparatorType.DASHED_LINE_WITH_SCISSORS, SeparatorType.DOTTED_LINE_WITH_SCISSORS]

        line_style = None
        line_width = 0
        if separator_type in [SeparatorType.DASHED_LINE, SeparatorType.DASHED_LINE_WITH_SCISSORS]:
            line_style = LineStyle.DASHED
            line_width = 0.6
        elif separator_type in [SeparatorType.DOTTED_LINE, SeparatorType.DOTTED_LINE_WITH_SCISSORS]:
            line_style = LineStyle.DOTTED
            line_width = 0.75
        else:
            line_style = LineStyle.SOLID
            line_width = 0.5

        self._graphics.set_transformation(0, 0, 0, 1, 1)

        # draw vertical separator line between receipt and payment part
        self._graphics.start_path()
        self._graphics.move_to(RECEIPT_WIDTH, 0)
        if has_scissors:
            self._graphics.line_to(RECEIPT_WIDTH, SLIP_HEIGHT - 8)
            self._graphics.move_to(RECEIPT_WIDTH, SLIP_HEIGHT - 5)
        self._graphics.line_to(RECEIPT_WIDTH, SLIP_HEIGHT)

        # draw horizontal separator line between bill and rest of A4 sheet
        if output_size != OutputSize.QR_BILL_ONLY:
            self._graphics.move_to(0, SLIP_HEIGHT)
            if has_scissors:
                self._graphics.line_to(5, SLIP_HEIGHT)
                self._graphics.move_to(8, SLIP_HEIGHT)
            self._graphics.line_to(SLIP_WIDTH, SLIP_HEIGHT)
        self._graphics.stroke_path(line_width, 0, line_style, False)

        # draw scissors
        if has_scissors:
            self.draw_scissor(RECEIPT_WIDTH, SLIP_HEIGHT - 5, 0)
            if output_size != OutputSize.QR_BILL_ONLY:
                self.draw_scissor(5, SLIP_HEIGHT, 90.0)

        # Borders
        if vertical_border_type in [VerticalBorderType.LEFT, VerticalBorderType.BOTH]:
            self._graphics.start_path()
            self._graphics.move_to(0, 0)
            self._graphics.line_to(0, SLIP_HEIGHT)  # SLIP_HEIGHT)
            self._graphics.stroke_path(0.5, 0, LineStyle.DASHED, False)
        if vertical_border_type in [VerticalBorderType.RIGHT, VerticalBorderType.BOTH]:
            self._graphics.start_path()
            self._graphics.move_to(SLIP_WIDTH, 0)
            self._graphics.line_to(SLIP_WIDTH, SLIP_HEIGHT)  # SLIP_HEIGHT)
            self._graphics.stroke_path(0.5, 0, LineStyle.DASHED, False)

    def draw_scissor(self, x: float, y: float, angle: float):
        """Draw a scissor."""
        self.draw_scissors_blade(x, y, 3, angle, False)
        self.draw_scissors_blade(x, y, 3, angle, True)

    def draw_scissors_blade(self, x: float, y: float, size: float, angle: float, mirrored: bool):
        """Draw a scissor blade (i.e. on half of a scissor)."""
        scale = size / 476.0
        x_offset = 0.36 * size
        y_offset = -1.05 * size
        # Compute the transformations to be applied
        (new_x, new_y) = Affine.translation(x, y) * Affine.rotation(angle) * Affine.translation(x_offset if mirrored else -x_offset, y_offset) * Affine.scale(scale) * (1, 1)

        self._graphics.set_transformation(new_x, new_y, angle, -scale if mirrored else scale, scale)

        self._graphics.start_path()
        self._graphics.move_to(46.48, 126.784)
        self._graphics.cubic_curve_to(34.824, 107.544, 28.0, 87.924, 28.0, 59.0)
        self._graphics.cubic_curve_to(28.0, 36.88, 33.387, 16.436, 42.507, -0.124)
        self._graphics.line_to(242.743, 326.63)
        self._graphics.cubic_curve_to(246.359, 332.53, 254.836, 334.776, 265.31, 328.678)
        self._graphics.cubic_curve_to(276.973, 321.89, 290.532, 318.0, 305.0, 318.0)
        self._graphics.cubic_curve_to(348.63, 318.0, 384.0, 353.37, 384.0, 397.0)
        self._graphics.cubic_curve_to(384.0, 440.63, 348.63, 476.0, 305.0, 476.0)
        self._graphics.cubic_curve_to(278.066, 476.0, 254.28, 462.521, 240.02, 441.94)
        self._graphics.line_to(46.48, 126.785)
        self._graphics.close_subpath()
        self._graphics.move_to(303.5, 446.0)
        self._graphics.cubic_curve_to(330.286, 446.0, 352.0, 424.286, 352.0, 397.5)
        self._graphics.cubic_curve_to(352.0, 370.714, 330.286, 349.0, 303.5, 349.0)
        self._graphics.cubic_curve_to(276.714, 349.0, 255.0, 370.714, 255.0, 397.5)
        self._graphics.cubic_curve_to(255.0, 424.286, 276.714, 446.0, 303.5, 446.0)
        self._graphics.close_subpath()
        self._graphics.fill_path(0, True)

    def draw_corners(self, x: float, y: float, width: float, height: float):
        CORNER_STROKE_WIDTH = 0.75
        lwh = CORNER_STROKE_WIDTH * 0.5 / 72 * 25.4
        s = 3.0

        self._graphics.start_path()

        self._graphics.move_to(x + lwh, y + s)
        self._graphics.line_to(x + lwh, y + lwh)
        self._graphics.line_to(x + s, y + lwh)

        self._graphics.move_to(x + width - s, y + lwh)
        self._graphics.line_to(x + width - lwh, y + lwh)
        self._graphics.line_to(x + width - lwh, y + s)

        self._graphics.move_to(x + width - lwh, y + height - s)
        self._graphics.line_to(x + width - lwh, y + height - lwh)
        self._graphics.line_to(x + width - s, y + height - lwh)

        self._graphics.move_to(x + s, y + height - lwh)
        self._graphics.line_to(x + lwh, y + height - lwh)
        self._graphics.line_to(x + lwh, y + height - s)

        self._graphics.stroke_path(CORNER_STROKE_WIDTH, 0, LineStyle.SOLID, False)

    def draw_label(self, label_key: str):
        self._graphics.put_text(MLT.get_text(label_key), 0, self._y_pos, self._label_font_size, True)
        self._y_pos -= self._line_spacing

    def draw_label_and_text(self, label_key: str, text: str):
        """Draws a label and a single line of text at (0, yPos) and advances vertically.

        yPos is taken as the baseline for the text.
        """
        self.draw_label(label_key)
        self._graphics.put_text(text, 0, self._y_pos, self._text_font_size, False)
        self._y_pos -= self._line_spacing + self._extra_spacing

    def draw_label_and_text_lines(self, label_key: str, text_lines: List[str]):
        """Draws a label and a multiple lines of text at (0, yPos) and advances vertically.

        yPos is taken as the baseline for the text.
        """
        self.draw_label(label_key)
        leading: float = self._line_spacing - self._graphics.get_line_height(self._text_font_size)
        self._graphics.put_text_lines(text_lines, 0, self._y_pos, self._text_font_size, leading)
        spacing = len(text_lines) * self._line_spacing + self._extra_spacing
        self._y_pos -= spacing

    def prepare_text(self):
        account = iban.format(self._bill.account)
        self._account_payable_to = f"{account}\n{self.format_address_for_display(self._bill.creditor)}"
        self._reference = self.format_reference_number(self._bill.reference)
        info = self._bill.unstructured_message

        if self._bill._bill_information is not None:
            if info is None:
                info = self._bill.bill_information
            else:
                info = f"{info}\n{self._bill.bill_information}"

        if info is not None:
            self._additional_info = info

        if self._bill.debtor is not None:
            self._payable_by = self.format_address_for_display(self._bill.debtor)

        if self._bill.amount is not None:
            self._amount = f"{self._bill.amount:,.2f}".replace(",", " ")

    def prepare_reduced_receipt_text(self, reduce_both: bool):
        if reduce_both:
            account = iban.format(self._bill.account)
            self._account_payable_to = account + "\n" + self.format_address_for_display(self._bill.creditor.create_reduced_address())

        if self._bill.debtor is not None:
            self._payable_by = self.format_address_for_display(self._bill.debtor.create_reduced_address())

    @staticmethod
    def format_address_for_display(address: Address) -> str:
        text = []
        text.append(address.name)
        if address.type == AddressType.STRUCTURED:
            street = address.street
            if street is not None:
                text.append("\n")
                text.append(street)
            house_no = address.house_no
            if house_no is not None:
                text.append(" " if street is not None else "\n")
                text.append(house_no)
            text.append("\n")
            # 0.25 if address.country_code in ['CH', 'LI']:
            text.append(address.country_code)
            text.append(" ")
            text.append(address.postal_code)
            text.append(" ")
            text.append(address.town)
        elif address.type == AddressType.COMBINED_ELEMENTS:
            if address.address_line1 is not None:
                text.append("\n")
                text.append(address.address_line1)
            text.append("\n")
            # 0.25 if address.country_code in ['CH', 'LI']:
            text.append(address.country_code)
            text.append(" ")
            text.append(address.address_line2)

        # Replace 'None' values by ""
        text = ["" if item is None else item for item in text]
        return "".join(list(map(str, text)))

    def format_reference_number(self, ref_no: str) -> str:
        if ref_no is None:
            return None
        if ref_no.startswith("RF"):
            # same format as IBAN
            return iban.format(ref_no)
        return esr.format(ref_no)

    def break_lines(self, max_width: float):
        # Prepare the text (by breaking it into lines where necessary)
        font_size = self._text_font_size * 1.03
        self._account_payable_to_lines = self._graphics.split_lines(self._account_payable_to, max_width * MM_TO_PT, font_size)
        if self._additional_info is not None:
            self._additional_info_lines = self._graphics.split_lines(self._additional_info, max_width * MM_TO_PT, font_size)
        if self._payable_by is not None:
            self._payable_by_lines = self._graphics.split_lines(self._payable_by, max_width * MM_TO_PT, font_size)

    def truncate_text(self, text: str, max_width: float, font_size: float) -> str:
        ELLIPSIS_WIDTH = 0.3528  # mm * font size
        ELLIPSIS_CHAR = "…"

        if self._graphics.get_text_width(text, font_size, False) < max_width:
            return text

        lines = self._graphics.split_lines(text, max_width - font_size * ELLIPSIS_WIDTH, font_size)
        return lines[0] + ELLIPSIS_CHAR

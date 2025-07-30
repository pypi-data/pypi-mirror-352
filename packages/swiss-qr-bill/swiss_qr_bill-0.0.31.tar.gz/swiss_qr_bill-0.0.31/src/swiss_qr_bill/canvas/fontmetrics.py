# -*- coding: utf-8 -*-
#
# Swiss QR Bill Generator
# Copyright (c) 2017 Manuel Bleichenbacher
# Licensed under MIT License
# https:#opensource.org/licenses/MIT
#
# Translated from Java m.mohnhaupt@bluewin.ch
from typing import Final, List

from .char_width_data import CharWidthData


class FontMetrics:
    PT_TO_MM: Final = 25.4 / 72

    def __init__(self, font_family_list: str, is_bold=False) -> None:
        self._font_family_list = font_family_list
        self.first_font_family = self._get_first_font_family(font_family_list).lower()

        if self.first_font_family == 'arial':
            self.char_width_x20_x7F = CharWidthData.ARIAL_NORMAL_20_7F
            self.char_width_xA0_xFF = CharWidthData.ARIAL_NORMAL_A0_FF
            self.char_default_width = CharWidthData.ARIAL_NORMAL_DEFAULT_WIDTH
            self.bold_char_width_x20_x7F = CharWidthData.ARIAL_BOLD_20_7F
            self.bold_char_width_xA0_xFF = CharWidthData.ARIAL_BOLD_A0_FF
            self.bold_char_default_width = CharWidthData.ARIAL_BOLD_DEFAULT_WIDTH
        elif self.first_font_family == 'liberation sans':
            self.char_width_x20_x7F = CharWidthData.LIBERATION_SANS_NORMAL_20_7F
            self.char_width_xA0_xFF = CharWidthData.LIBERATION_SANS_NORMAL_A0_FF
            self.char_default_width = CharWidthData.LIBERATION_SANS_NORMAL_DEFAULT_WIDTH
            self.bold_char_width_x20_x7F = CharWidthData.LIBERATION_SANS_BOLD_20_7F
            self.bold_char_width_xA0_xFF = CharWidthData.LIBERATION_SANS_BOLD_A0_FF
            self.bold_char_default_width = CharWidthData.LIBERATION_SANS_BOLD_DEFAULT_WIDTH
        elif self.first_font_family == 'frutiger':
            self.char_width_x20_x7F = CharWidthData.FRUTIGER_NORMAL_20_7F
            self.char_width_xA0_xFF = CharWidthData.FRUTIGER_NORMAL_A0_FF
            self.char_default_width = CharWidthData.FRUTIGER_NORMAL_DEFAULT_WIDTH
            self.bold_char_width_x20_x7F = CharWidthData.FRUTIGER_BOLD_20_7F
            self.bold_char_width_xA0_xFF = CharWidthData.FRUTIGER_BOLD_A0_FF
            self.bold_char_default_width = CharWidthData.FRUTIGER_BOLD_DEFAULT_WIDTH
        else:
            self.char_width_x20_x7F = CharWidthData.HELVETICA_NORMAL_20_7F
            self.char_width_xA0_xFF = CharWidthData.HELVETICA_NORMAL_A0_FF
            self.char_default_width = CharWidthData.HELVETICA_NORMAL_DEFAULT_WIDTH
            self.bold_char_width_x20_x7F = CharWidthData.HELVETICA_BOLD_20_7F
            self.bold_char_width_xA0_xFF = CharWidthData.HELVETICA_BOLD_A0_FF
            self.bold_char_default_width = CharWidthData.HELVETICA_BOLD_DEFAULT_WIDTH

        if is_bold:
            self.char_width_x20_x7F = self.bold_char_width_x20_x7F
            self.char_width_xA0_xFF = self.bold_char_width_xA0_xFF
            self.char_default_width = self.bold_char_default_width

    @property
    def font_family_list(self) -> str:
        return self._font_family_list

    def get_ascender(self, font_size: int) -> float:
        """Distance between baseline and top of highest letter.

        * font_size : the font size (in pt)
        * returns the distance (in mm)
        """
        return font_size * 0.8 * self.PT_TO_MM

    def get_descender(self, font_size: int) -> float:
        """Distance between baseline and bottom of letter extending the farthest below the baseline.

        * font_size : the font size (in pt)
        * returns the distance (in mm)
        """
        return font_size * 0.2 * self.PT_TO_MM

    def get_line_height(self, font_size: int) -> float:
        """Distance between the baselines of two consecutive text lines.

        * font_size : the font size (in pt)
        * returns the distance (in mm)
        """
        return font_size * self.PT_TO_MM

    def split_lines(self, text: str, max_length: float, font_size: int) -> List[str]:
        """Splits the text into lines.

        If a line would exceed the specified maximum length, line breaks are
        inserted. Newlines are treated as fixed line breaks.

        Yes, this code has a cognitive complexity of 37. Deal with it."""

        lines: List[str] = []
        max = int(max_length * 1000 / font_size)
        str_len = len(text)  # length of line
        pos = 0  # current position (0 ..< end)
        line_start_pos = 0  # start position of current line
        line_width = 0  # current line width (in AFM metric)
        add_empty_line = True  # flag if an empty line should be added as the last line
        # iterate over all characters
        while pos < str_len:
            # get current character
            ch = text[pos]
            # skip leading white space at start of current line
            if ch == ' ' and pos == line_start_pos:
                line_start_pos += 1
                pos += 1
                continue

            # add width of character
            line_width += self._get_char_width(ch)
            add_empty_line = False

            # line break is need if the maximum width has been reached
            # or if an explicit line break has been encountered
            if ch == '\n' or line_width > max:
                # find the position for the line break
                if ch == '\n':
                    break_pos = pos
                else:
                    # locate the previous space on the line
                    space_pos = pos - 1
                    while space_pos > line_start_pos:
                        if text[space_pos] == ' ':
                            break
                        space_pos -= 1

                    # if space was found, it's the break position
                    if space_pos > line_start_pos:
                        break_pos = space_pos
                    else:
                        # if no space was found, forcibly break word
                        if pos > line_start_pos:
                            break_pos = pos
                        else:
                            break_pos = line_start_pos + 1  # at least one character

                # add line to result
                self._add_result_line(lines, text, line_start_pos, break_pos)

                # setup start of new line
                line_start_pos = break_pos
                if ch == '\n':
                    line_start_pos = break_pos + 1
                    add_empty_line = True
                pos = line_start_pos
                line_width = 0
            else:
                # no line break needed; progress one character
                pos += 1

        # complete the last line
        if pos > line_start_pos:
            self._add_result_line(lines, text, line_start_pos, pos)
        elif add_empty_line:
            lines.append("")

        return lines

    def get_text_width(self, text: str, font_size: int, is_bold: bool) -> int:
        """Returns the width of the specified text for the specified font size."""
        if is_bold:
            bold_metrics = FontMetrics(self._font_family_list, is_bold=True)
            return bold_metrics.get_text_width(text, font_size, False)

        width = 0
        for ch in text:
            width += self._get_char_width(ch)
        return width * font_size / 1000 * self.PT_TO_MM

    def _get_char_width(self, ch: str) -> int:
        width = 0
        ch = ord(ch)
        if ch >= 0x20 and ch <= 0x7f:
            width = self.char_width_x20_x7F[ch - 0x20]
        elif ch >= 0xa0 and ch <= 0xff:
            width = self.char_width_xA0_xFF[ch - 0xa0]

        if width == 0:
            width = self.char_default_width
        return width

    @staticmethod
    def _add_result_line(lines: List[str], text: str, start: int, end: int):
        """Add the specified text range to the resulting lines.

        Trim trailing white space

        * lines : resulting lines array
        * text : text
        * start : start of text range (including)
        * end :   end of text range (excluding)
        """
        lines.append(text[start:end].strip())

    @staticmethod
    def _get_first_font_family(font_family_list: str) -> str:
        return font_family_list.split(',')[0].strip(' "')

from abc import ABC, abstractmethod
from typing import List

from ..generator.enums import LineStyle
from .fontmetrics import FontMetrics


class CanvasBase(ABC):
    """Abstract base class for simplified implementation of Canvas classes."""
    MM_TO_PT = 72 / 25.4
    VERSION = '1.1'
    font_metrics: FontMetrics = None

    @abstractmethod
    def get_content() -> str:
        """Closes the Canvas an gets its content.

        Returns:
            str: the content
        """
        pass

    @abstractmethod
    def set_transformation(translate_x: float, translate_y: float, rotate: float, scale_x: float, scale_y: float) -> None:
        """Sets a translation, rotation and scaling for the subsequent operations.

        Before a new translation is applied, the coordinate system is reset to it's original state.

        The transformations are applied in the order translation, rotation, scaling.

        Args:
            translate_x (float): translation in x direction (in mm)
            translate_y (float): translation in y direction (in mm)
            rotate (float): rotation angle, in radians
            scale_x (float): scale factor in x direction (1.0 = no scaling)
            scale_y (float): scale factor in y direction (1.0 = no scaling)
        """
        pass

    @abstractmethod
    def put_text(self, text: str, x: float, y: float, font_size: int, is_bold: bool) -> None:
        """Adds text to the graphics.

        The text position refers to the left most point on the text's baseline.

        Args:
            text (str): the text
            x (float): x position of the text's start (in mm)
            y (float): y position of the text's top (in mm)
            font_size (int): the font size (in pt)
            is_bold (bool): indicates if the text is in bold or regular weight
        """
        pass

    @abstractmethod
    def start_path() -> None:
        """Starts a path that can be filled or stroked.
        """
        pass

    @abstractmethod
    def move_to(x: float, y: float) -> None:
        """Moves the current point of the open path to the specified position.

        Args:
            x (float): x coordinate of position
            y (float): y coordinate of position
        """
        pass

    @abstractmethod
    def line_to(x: float, y: float) -> None:
        """Adds a line segment to the open path from the previous point to the specified position.

        Args:
            x (float): x coordinate of position
            y (float): y coordinate of position
        """
        pass

    @abstractmethod
    def cubic_curve_to(x1: float, y1: float, x2: float, y2: float, x: float, y: float) -> None:
        """Adds a cubic Bézier curve to the open path going from the previous point to the specified position. Two control points control the curve.

        Args:
            x1 (float): x coordinate of first control point
            y1 (float): y coordinate of first control point
            x2 (float): x coordinate of second control point
            y2 (float): y coordinate of second control point
            x (float): x coordinate of position
            y (float): y coordinate of position
        """
        pass

    @abstractmethod
    def add_rectangle(x: float, y: float, width: float, height: float) -> None:
        """Adds a rectangle to the path.

        Args:
            x (float): the rectangle's left position (in mm)
            y (float): the rectangle's top position (in mm)
            width (float): the rectangle's width (in mm)
            height (float): rectangle's height (in mm)
        """
        pass

    @abstractmethod
    def close_subpath() -> None:
        """Closes the current subpath.
        """
        pass

    @abstractmethod
    def fill_path(color: int, smoothing: bool) -> None:
        """Fills the current path and ends it.

        Args:
            color (int): the fill color (expressed similar to HTML, e.g. 0xffffff for white)
            smoothing (bool): True for using smoothing techniques such as antialiasing, False otherwise
        """
        pass

    @abstractmethod
    def stroke_path(stroke_width: float, color: int, line_style: LineStyle, smoothing: bool) -> None:
        """Strokes the current path and ends it.

        Args:
            stroke_width (float): the stroke width (in pt)
            color (int): the stroke color (expressed similar to HTML, e.g. 0xffffff for white)
            line_style (LineStyle): the line style
            smoothing (bool): True for using smoothing techniques such as antialiasing, False otherwise
        """
        pass

    def setup_font_metrics(self, font_family_list: str):
        """Initializes the font metrics information for the specified font. The know font in the specified list of fonts is used.

        Args:
            font_family_list (str): list of font families
        """
        self.font_metrics = FontMetrics(font_family_list)

    def put_text_lines(self, lines: List[str], x: float, y: float, font_size: int, leading: float) -> None:
        """Adds several lines of text to the graphics.

        The text position refers to the left most point on the baseline of the first text line. 
        Additional lines then follow below.

        Args:
            lines (List[str]): the text lines
            x (float): x position of the text's start (in mm)
            y (float): y position of the text's start (in mm)
            font_size (int): the font size (in pt)
            leading (float): additional vertical space between text lines (in mm)
        """
        for line in lines:
            self.put_text(line, x, y, font_size, False)
            y -= (self.font_metrics.get_line_height(font_size) + leading)

    def split_lines(self, text, max_length, font_size) -> List[str]:
        return self.font_metrics.split_lines(text, max_length, font_size)

    def get_ascender(self, font_size) -> float:
        return self.font_metrics.get_ascender(font_size)

    def get_descender(self, font_size) -> float:
        return self.font_metrics.get_descender(font_size)

    def get_line_height(self, font_size) -> float:
        return self.font_metrics.get_line_height(font_size)

    def get_text_width(self, text, font_size, is_bold) -> float:
        return self.font_metrics.get_text_width(text, font_size, is_bold)

    @staticmethod
    def escape_XML(text: str) -> str:
        """Replace special characters by XML entities.

        Args:
            text (str): the text to escape

        Returns:
            str: the escaped text
        """
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")

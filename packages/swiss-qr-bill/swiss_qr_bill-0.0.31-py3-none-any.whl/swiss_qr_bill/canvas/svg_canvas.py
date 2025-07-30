import io

from ..generator.enums import LineStyle
from .canvas_base import CanvasBase

_XML_HEADER = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
_XML_DOCTYPE = '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">'
_SVG_TITLE = '<title>Swiss QR Bill</title>'


def _format_coord(value: float) -> str:
    return f'{value * CanvasBase.MM_TO_PT:.3f}'


class SVGCanvas(CanvasBase):

    def __init__(self, width, height, font_family_list) -> None:
        self.setup_font_metrics(font_family_list)
        self._buffer = io.StringIO()
        self._content = None
        self._is_in_group = False
        self._path = []
        self.is_first_move_in_path = False
        self._last_position_X = 0.0
        self._last_position_Y = 0.0

        vb_width = width * CanvasBase.MM_TO_PT
        vb_height = height * CanvasBase.MM_TO_PT
        font_family = self.escape_XML(font_family_list)

        # Headers / title
        self._buffer.write(f'{_XML_HEADER} {_XML_DOCTYPE} ')
        self._buffer.write(f'<svg width="{width:.0f}mm" height="{height:.0f}mm" version="{CanvasBase.VERSION}" viewBox="0 0 {vb_width:.3f} {vb_height:.3f}" xmlns="http://www.w3.org/2000/svg">')
        self._buffer.write(f'<g font-family="{font_family}" transform="translate(0 {vb_height:.3f})">')
        self._buffer.write(f'{_SVG_TITLE}')
        self._buffer.write(f'<rect x="0" y="-{vb_height:.3f}" width="{vb_width:.3f}" height="{vb_height:.3f}" fill="#ffffff" stroke="#ffffff" stroke-width="0"/>')

    def get_content(self) -> str:
        self.close()
        return self._content

    def close(self) -> None:
        if self._is_in_group:
            self._buffer.write('</g>')
            self._is_in_group = False

        if self._buffer is not None:
            self._buffer.write('</g>')
            self._buffer.write('</svg>')
            self._content = self._buffer.getvalue()
            self._buffer.close()
            self._buffer = None

    def start_path(self) -> None:
        self._is_first_move_in_path = True
        self._path = []

    def move_to(self, x, y) -> None:
        y = -y
        if self._is_first_move_in_path:
            self._path.append(f'M{_format_coord(x)},{_format_coord(y)}')
            self._is_first_move_in_path = False
        else:
            self._path.append(f'm{_format_coord(x-self._last_position_X)},{_format_coord(y-self._last_position_Y)}')
        self._last_position_X = x
        self._last_position_Y = y

    def line_to(self, x, y) -> None:
        y = -y
        self._path.append(f'l{_format_coord(x-self._last_position_X)},{_format_coord(y-self._last_position_Y)}')
        self._last_position_X = x
        self._last_position_Y = y

    def cubic_curve_to(self, x1, y1, x2, y2, x, y) -> None:
        y1, y2, y = -y1, -y2, -y
        self._path.append(f"""c{_format_coord(x1 - self._last_position_X)},{_format_coord(y1 - self._last_position_Y)},
            {_format_coord(x2 - self._last_position_X)},{_format_coord(y2 - self._last_position_Y)},
            {_format_coord(x - self._last_position_X)},{_format_coord(y - self._last_position_Y)}""")
        self._last_position_X = x
        self._last_position_Y = y

    def add_rectangle(self, x, y, width, height) -> None:
        self.move_to(x, y + height)
        self._path.append(f'h{_format_coord(width)}v{_format_coord(height)}h{_format_coord(-width)}z')

    def close_subpath(self) -> None:
        self._path.append('z')

    def fill_path(self, color, smoothing) -> None:
        self._buffer.write(f'<path fill="#{self._format_color(color)}')
        if not smoothing:
            self._buffer.write('" shape-rendering="crispEdges')
        data = ''.join(self._path).replace(' ', '').replace('\n', '')
        self._buffer.write(f'" d="{data}"/>')
        self._path = None
        self._is_first_move_in_path = True

    def stroke_path(self, stroke_width: float, color: int, line_style: LineStyle, smoothing: bool) -> None:
        self._buffer.write(f'<path stroke="#{self._format_color(color)}')
        if stroke_width != 1:
            self._buffer.write(f'" stroke-width="{stroke_width:.2f}')
        if line_style == LineStyle.DASHED:
            self._buffer.write(f'" stroke-dasharray="{stroke_width*4:.2f}')
        elif line_style == LineStyle.DOTTED:
            self._buffer.write(f'" stroke-linecap="round" stroke-dasharray="0 {stroke_width*3:.2f}')
        if not smoothing:
            self._buffer.write('" shape-rendering="crispEdges')
        data = ''.join(self._path).replace(' ', '').replace('\n', '')
        self._buffer.write(f'" fill="none" d="{data}"/>')
        self._path = None
        self._is_first_move_in_path = True

    def put_text(self, text, x, y, font_size, is_bold=False) -> None:
        y = -y
        self._buffer.write(f'<text x="{_format_coord(x)}" y="{_format_coord(y)}" font-size="{font_size}"')
        if is_bold:
            self._buffer.write(' font-weight="bold"')
        self._buffer.write(f'>{CanvasBase.escape_XML(text)}</text>')

    def set_transformation(self, translate_x: float, translate_y: float, rotate: float, scale_x: float, scale_y: float) -> None:
        if self._is_in_group:
            self._buffer.write("</g>")
            self._is_in_group = False
        if translate_x != 0 or translate_y != 0 or scale_x != 1 or scale_y != 1:
            self._buffer.write(f'<g transform="translate({_format_coord(translate_x)} {_format_coord(-translate_y)}')
            if rotate != 0:
                self._buffer.write(f') rotate({-rotate:.2f}')
            if scale_x != 1 or scale_y != 1:
                self._buffer.write(f') scale({scale_x:.3f}')
                if scale_y != scale_x:
                    self._buffer.write(f' {scale_y:.3f}')
            self._buffer.write(')">')
            self._is_in_group = True

    def _format_color(self, color):
        return f'{color:06x}'

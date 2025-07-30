from .enums import OutputSize, Language, SeparatorType, GraphicsFormat, VerticalBorderType


class BillFormat:
    DEFAULT_MARGIN_WIDTH = 5.0

    def __init__(self, *args) -> None:
        self._output_size = OutputSize.QR_BILL_ONLY
        self._language = Language.EN
        self._separator_type = SeparatorType.DASHED_LINE_WITH_SCISSORS
        self._vertical_border_type = VerticalBorderType.NONE
        self._font_family = 'Helvetica, Arial, Liberation Sans'
        self._graphics_format = GraphicsFormat.SVG
        self._resolution = 144
        self._margin_left = BillFormat.DEFAULT_MARGIN_WIDTH
        self._margin_right = BillFormat.DEFAULT_MARGIN_WIDTH

        # Copy constructor: creates a copy of the specified format
        if len(args) == 1 and isinstance(args[0], BillFormat):
            format: BillFormat = args[0]
            self._output_size = format._output_size
            self._language = format._language
            self._separator_type = format._separator_type
            self._vertical_border_type = format._vertical_border_type
            self._font_family = format._font_family
            self._graphics_format = format._graphics_format
            self._resolution = format._resolution
            self._margin_left = format._margin_left
            self._margin_right = format._margin_right

    @property
    def output_size(self):
        return self._output_size

    @output_size.setter
    def output_size(self, value: OutputSize):
        self._output_size = value

    @property
    def language(self):
        return self._language

    @language.setter
    def language(self, value: Language):
        self._language = value

    @property
    def separator_type(self):
        return self._separator_type

    @separator_type.setter
    def separator_type(self, value: SeparatorType):
        self._separator_type = value

    @property
    def vertical_border_type(self):
        return self._vertical_border_type

    @vertical_border_type.setter
    def vertical_border_type(self, value: VerticalBorderType):
        self._vertical_border_type = value

    @property
    def font_family(self):
        return self._font_family

    @font_family.setter
    def font_family(self, value: str):
        self._font_family = value

    @property
    def graphics_format(self):
        return self._graphics_format

    @graphics_format.setter
    def graphics_format(self, value: GraphicsFormat):
        self._graphics_format = value

    @property
    def resolution(self):
        return self._resolution

    @resolution.setter
    def resolution(self, value: int):
        self._resolution = value

    @property
    def margin_left(self):
        return self._margin_left

    @margin_left.setter
    def margin_left(self, value: float):
        self._margin_left = value

    @property
    def margin_right(self):
        return self._margin_right

    @margin_right.setter
    def margin_right(self, value: float):
        self._margin_right = value

    def __str__(self) -> str:
        return f'''
        BillFormat
            output_size={self._output_size},
            language={self._language}
            separator_type={self._separator_type}
            font_family={self._font_family}
            graphics_format={self._graphics_format}
            resolution={self._resolution}
            margin_left={self._margin_left}
            margin_right={self._margin_right}
        '''

from enum import Enum, auto


class LineStyle(Enum):
    """The line styles being used."""
    SOLID = auto()  # Solid line
    DASHED = auto()  # Dashed line (dashes are about 4 times the line width long and apart)
    DOTTED = auto()  # Dotted line (dots are spaced 3 times the line width apart)


class Language(Enum):
    EN = auto()
    FR = auto()
    DE = auto()
    IT = auto()
    RM = auto()


class GraphicsFormat(Enum):
    PDF = auto()
    SVG = auto()
    PNG = auto()


class OutputSize(Enum):
    # A4 sheet in portrait orientation. The QR bill is at the bottom.
    A4_PORTRAIT_SHEET = auto()
    # QR bill only (about 105 by 210 mm).
    # <p>
    # This size is suitable if the QR bill has not horizontal line.
    # If the horizontal line is needed and the A4 sheet size is not
    # suitable, use {@link #QR_BILL_EXTRA_SPACE} instead.
    # </p>
    QR_BILL_ONLY = auto()
    # QR code only (46 by 46 mm).
    QR_CODE_ONLY = auto()
    # QR bill only with additional space at the top for the horizontal line (about 110 by 210 mm).
    # <p>
    # The extra 5 mm at the top create space for the horizontal line and
    # optionally for the scissors.
    # </p>
    QR_BILL_EXTRA_SPACE = auto()


class VerticalBorderType(Enum):
    NONE = auto()
    LEFT = auto()
    RIGHT = auto()
    BOTH = auto()


class SeparatorType(Enum):
    # No separators are drawn (because paper has perforation)
    NONE = auto()
    # Solid lines are drawn
    SOLID_LINE = auto()
    # Solid lines with a scissor symbol are drawn
    SOLID_LINE_WITH_SCISSORS = auto()
    # Dashed lines are drawn
    DASHED_LINE = auto()
    # Dashed lines with a scissor symbol are drawn
    DASHED_LINE_WITH_SCISSORS = auto()
    # Dotted lines are drawn
    DOTTED_LINE = auto()
    # Dotted lines with a scissor symbol are drawn
    DOTTED_LINE_WITH_SCISSORS = auto()


class AddressType(Enum):
    UNDETERMINED = auto()
    STRUCTURED = auto()
    COMBINED_ELEMENTS = auto()
    CONFLICTING = auto()


class ReferenceType(Enum):
    REFERENCE_TYPE_NO_REF = 'NON'
    REFERENCE_TYPE_QR_REF = 'QRR'
    REFERENCE_TYPE_CRED_REF = 'SCOR'

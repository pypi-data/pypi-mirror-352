import typing
from qtpy.QtGui import QColor
import numpy as np


class Color:
    r: int
    g: int
    b: int
    a: int

    @typing.overload
    def __init__(self, r: int, g: int, b: int, a: int = 255):
        '''
        Initialize Colors with RGB or RGBA integer values ranging from 0 to 255.
        '''
    
    @typing.overload
    def __init__(self, r: float, g: float, b: float, a: float = 1.0):
        '''
        Initialize Colors with RGB or RGBA floating values ranging from 0.0 to 1.0.
        '''
    
    @typing.overload
    def __init__(self, hexa: str):
        '''
        Initialize colors from hex values.
        The valid formats incluce RGB (#FF0000 for example)
        and RGBA (#FF0000FF for example)
        '''

    @typing.overload
    def __init__(self, qcolor: QColor):
        '''
        Initialize the color class with an instance of QColor
        '''
    
    @typing.overload
    def __init__(self, color: "Color"):
        '''
        Initialize the color class with an instance it's own class
        '''
    
    @typing.overload
    def __init__(self):
        '''
        Initialize an empty black color
        '''

    def __init__(self, *args):

        all_int = all([isinstance(i, int) for i in args])
        all_float = all([isinstance(i, float) for i in args])

        if len(args) == 0:
            self.from_rgba(0, 0, 0, 255)

        elif len(args) == 1 and isinstance(args[0], str):
            self.from_hex(*args)
        
        elif len(args) == 1 and isinstance(args[0], QColor):
            self.from_qcolor(*args)
        
        elif len(args) == 1 and isinstance(args[0], Color):
            self.from_color(*args)

        elif len(args) in [3, 4] and all_int:
            self.from_rgba(*args)

        elif len(args) in [3, 4] and all_float:
            self.from_rgba_f(*args)

        else:
            raise ValueError("Invalid input values")

    def from_rgb(self, r: int, g: int, b: int) -> "Color":
        return self.from_rgba(r, g, b)

    def from_rgba(self, r: int, g: int, b: int, a: int=255) -> "Color":
        self.r = int(np.clip(r, 0, 255))
        self.g = int(np.clip(g, 0, 255))
        self.b = int(np.clip(b, 0, 255))
        self.a = int(np.clip(a, 0, 255))
        return self

    def from_rgb_f(self, r: float, g: float, b: float) -> "Color":
        return self.from_rgba_f(r, g, b)

    def from_rgba_f(self, r: float, g: float, b: float, a: float = 1) -> "Color":
        return self.from_rgba(
            int(r * 255),
            int(g * 255),
            int(b * 255),
            int(a * 255),
        )

    def from_hex(self, color: str) -> "Color":
        color = color.lstrip('#')
        if len(color) == 6:
            r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
            return self.from_rgb(r, g, b)
        elif len(color) == 8:
            r, g, b, a = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16), int(color[6:8], 16)
            return self.from_rgba(r, g, b, a)
        raise ValueError("Invalid hex color format")

    def from_qcolor(self, color: QColor) -> "Color":
        return self.from_rgba(color.red(), color.green(), color.blue(), color.alpha())

    def from_color(self, color: "Color"):
        self.r = color.r
        self.g = color.g
        self.b = color.b
        self.a = color.a
        return self

    def to_rgb(self) -> tuple[int, int, int]:
        return (self.r, self.g, self.b)

    def to_rgba(self) -> tuple[int, int, int, int]:
        return (self.r, self.g, self.b, self.a)

    def to_rgb_f(self) -> tuple[float, float, float]:
        return ((self.r / 255), (self.g / 255), (self.b / 255))

    def to_rgba_f(self) -> tuple[float, float, float, float]:
        return ((self.r / 255), (self.g / 255), (self.b / 255), (self.a / 255))

    def to_hex(self) -> str:
        return (f'#{self.r:02X}{self.g:02X}{self.b:02X}')

    def to_hexa(self) -> str:
        return (f'#{self.r:02X}{self.g:02X}{self.b:02X}{self.a:02X}')

    def to_qt(self) -> QColor:
        return QColor(self.r, self.g, self.b, self.a)

    def copy(self):
        return Color(self.r, self.g, self.b, self.a)
    
    def apply_factor(self, factor: float|int):
        new_color = self.copy()
        new_color.r = int(np.clip(self.r*factor, 0, 255))
        new_color.g = int(np.clip(self.g*factor, 0, 255))
        new_color.b = int(np.clip(self.b*factor, 0, 255))

        return new_color


        

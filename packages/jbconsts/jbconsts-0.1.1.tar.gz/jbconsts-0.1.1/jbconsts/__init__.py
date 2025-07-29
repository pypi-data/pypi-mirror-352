"""General constant values shared by my packages"""

"""Constant values for the jbutils package"""

from jbutils.types import T


class STYLES:
    BG_RED = "background-color: #FF0000"
    BG_DARK_RED = "background-color: #8B0000"
    BG_GREEN = "background-color: #00FF00"
    BG_DARK_GREEN = "background-color: #006400"
    BG_YELLOW = "background-color: #FFFF00"
    BG_DARK_YELLOW = "background-color: #FFD700"
    BG_BLUE = "background-color: #0000FF"
    BG_DARK_BLUE = "background-color: #00008B"
    BG_CYAN = "background-color: #00FFFF"
    BG_DARK_CYAN = "background-color: #008B8B"
    BG_MAGENTA = "background-color: #FF00FF"
    BG_DARK_MAGENTA = "background-color: #8B008B"
    BG_WHITE = "background-color: #FFFFFF"
    BG_BLACK = "background-color: #000000"
    BG_GRAY = "background-color: #808080"
    BG_DARK_GRAY = "background-color: #A9A9A9"
    BG_LIGHT_GRAY = "background-color: #D3D3D3"
    BG_SILVER = "background-color: #C0C0C0"
    BG_GOLD = "background-color: #FFD700"
    BG_ORANGE = "background-color: #FFA500"
    BG_BROWN = "background-color: #A52A2A"
    BG_PINK = "background-color: #FFC0CB"
    BG_PURPLE = "background-color: #800080"
    BG_INDIGO = "background-color: #4B0082"
    BG_VIOLET = "background-color: #EE82EE"
    BG_LIME = "background-color: #00FF00"
    BG_OLIVE = "background-color: #808000"
    BG_TEAL = "background-color: #008080"
    BG_AQUA = "background-color: #00FFFF"
    BG_MAROON = "background-color: #800000"
    BG_NAVY = "background-color: #000080"

    @classmethod
    def get(cls, key: str, default: str = "") -> str:
        if hasattr(cls, key):

            return getattr(cls, key)
        return default


class COLORS:
    RED = "#FF0000"
    DARK_RED = "#8B0000"
    GREEN = "#00FF00"
    DARK_GREEN = "#006400"
    YELLOW = "#FFFF00"
    DARK_YELLOW = "#FFD700"
    BLUE = "#0000FF"
    DARK_BLUE = "#00008B"
    LIGHT_BLUE = "#6190ff"
    CYAN = "#00FFFF"
    DARK_CYAN = "#008B8B"
    MAGENTA = "#FF00FF"
    DARK_MAGENTA = "#8B008B"
    WHITE = "#FFFFFF"
    BLACK = "#000000"
    GRAY = "#808080"
    DARK_GRAY = "#A9A9A9"
    LIGHT_GRAY = "#D3D3D3"
    BLUE_GRAY = "#90909A"
    SILVER = "#C0C0C0"
    GOLD = "#FFD700"
    ORANGE = "#FFA500"
    BROWN = "#A52A2A"
    PINK = "#FFC0CB"
    PURPLE = "#800080"
    INDIGO = "#4B0082"
    VIOLET = "#EE82EE"
    LIME = "#00FF00"
    OLIVE = "#808000"
    TEAL = "#008080"
    AQUA = "#00FFFF"
    MAROON = "#800000"
    NAVY = "#000080"

    @classmethod
    def get(cls, key: str, default: str = "") -> str:
        if hasattr(cls, key):

            return getattr(cls, key)
        return default

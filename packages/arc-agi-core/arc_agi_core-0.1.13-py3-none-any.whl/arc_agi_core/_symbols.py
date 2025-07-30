from enum import Enum
from typing import Dict


class Symbol(Enum):
    """Represents the colors used in the grid."""

    ZERO = 0  # Background
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9


symbol_values = {symbol.value for symbol in Symbol}


ANSI_PALETTE: Dict[Symbol, str] = {
    # """Maps each color to its ANSI colored block character. """
    Symbol.ZERO: "\033[48;5;0m  \033[0m",  # Black
    Symbol.ONE: "\033[48;5;12m  \033[0m",  # Blue
    Symbol.TWO: "\033[48;5;9m  \033[0m",  # Red
    Symbol.THREE: "\033[48;5;10m  \033[0m",  # Green
    Symbol.FOUR: "\033[48;5;11m  \033[0m",  # Yellow
    Symbol.FIVE: "\033[48;5;8m  \033[0m",  # Grey
    Symbol.SIX: "\033[48;5;13m  \033[0m",  # Magenta
    Symbol.SEVEN: "\033[48;5;202m  \033[0m",  # Orange
    Symbol.EIGHT: "\033[48;5;14m  \033[0m",  # Cyan
    Symbol.NINE: "\033[48;5;1m  \033[0m",  # Brown
}

CSS_PALETTE: Dict[Symbol, str] = {
    # """Maps each color to its CSS color. "
    Symbol.ZERO: "black",
    Symbol.ONE: "blue",
    Symbol.TWO: "red",
    Symbol.THREE: "green",
    Symbol.FOUR: "yellow",
    Symbol.FIVE: "darkGrey",
    Symbol.SIX: "magenta",
    Symbol.SEVEN: "orange",
    Symbol.EIGHT: "cyan",
    Symbol.NINE: "brown",
}

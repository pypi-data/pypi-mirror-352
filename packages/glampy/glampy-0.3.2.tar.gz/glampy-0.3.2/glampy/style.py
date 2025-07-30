"""Utility functions for styling terminal output."""


# pylint: disable=too-few-public-methods
class Foreground_Colour:
    """Font foreground colours for use in terminal output."""

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    RESET = "\033[39m"


# pylint: disable=too-few-public-methods
class Background_Colour:
    """Font background colours for use in terminal output."""

    BLACK = "\033[40m"
    RED = "\033[41m"
    GREEN = "\033[42m"
    YELLOW = "\033[43m"
    BLUE = "\033[44m"
    MAGENTA = "\033[45m"
    CYAN = "\033[46m"
    WHITE = "\033[47m"
    RESET = "\033[49m"


# pylint: disable=too-few-public-methods
class Style:
    """Font styles and controls for use in terminal output."""

    BRIGHT = "\033[1m"
    DIM = "\033[2m"
    NORMAL = "\033[22m"
    RESET_ALL = "\033[0m"
    BOLD = "\033[1m"
    ITALIC = "\33[3m"
    UNDERLINE = "\033[4m"


# pylint: disable=too-few-public-methods
class Sign:
    """Unicode symbols for use in terminal output."""

    WARNING = "\u26A0"
    CRASH = "\U0001F4A5"
    PERSON = "\U0001F464"
    LOADING = "\U0001F5D8"
    CHECKMARK = "\u2713"
    TRIANGLE = "\u25B6"
    CIRCLE = "\u25EF"

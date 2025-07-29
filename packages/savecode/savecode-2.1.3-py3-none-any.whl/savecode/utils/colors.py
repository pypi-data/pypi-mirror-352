"""savecode/utils/colors.py - ANSI color codes for terminal output.

This module defines ANSI escape codes for text colors, background colors, and formatting styles.
It includes constants for common colors and formatting options, as well as a helper function
to apply one or more styles to a given text. This modular design facilitates future updates and additions.
"""

# Foreground color constants
BLACK: str = "\033[1;30m"
RED: str = "\033[1;31m"
GREEN: str = "\033[1;32m"
YELLOW: str = "\033[1;33m"
BLUE: str = "\033[1;34m"
MAGENTA: str = "\033[1;35m"
CYAN: str = "\033[1;36m"
WHITE: str = "\033[1;37m"

# Background color constants
BG_BLACK: str = "\033[40m"
BG_RED: str = "\033[41m"
BG_GREEN: str = "\033[42m"
BG_YELLOW: str = "\033[43m"
BG_BLUE: str = "\033[44m"
BG_MAGENTA: str = "\033[45m"
BG_CYAN: str = "\033[46m"
BG_WHITE: str = "\033[47m"

# Formatting options
BOLD: str = "\033[1m"
UNDERLINE: str = "\033[4m"
INVERT: str = "\033[7m"

# Reset code
RESET: str = "\033[0m"


def colored(text: str, *styles: str) -> str:
    """Apply given ANSI styles to the provided text and reset at the end.

    Args:
        text (str): The text to style.
        *styles (str): One or more ANSI style codes to apply.

    Returns:
        str: The styled text with a reset code appended.
    """
    return "".join(styles) + text + RESET


# End of savecode/utils/colors.py

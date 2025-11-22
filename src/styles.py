"""
UI styling constants and colour schemes for the Ping Monitor application.
"""
import platform


class Colours:
    """Colour palette for the application."""

    # Background colours - standard Windows grey
    BG_PRIMARY = "#F0F0F0"  # Standard Windows grey
    BG_SECONDARY = "#E0E0E0"
    BG_TERTIARY = "#D4D4D4"

    # Text colours
    TEXT_PRIMARY = "black"
    TEXT_SECONDARY = "#000000"
    TEXT_LIGHT = "#666666"

    # Status colours (for ping results) - more muted
    STATUS_EXCELLENT = "#008000"  # Dark green - < 20ms
    STATUS_GOOD = "#4C9900"       # Green - 20-60ms (fair)
    STATUS_FAIR = "#CC6600"       # Orange - 60-110ms (poor)
    STATUS_POOR = "#CC0000"       # Dark red - >= 110ms (bad)
    STATUS_FAILED = "#666666"     # Gray - failed ping

    # Border colours
    BORDER_LIGHT = "#CCCCCC"
    BORDER_MEDIUM = "#999999"
    BORDER_DARK = "#666666"


class Fonts:
    """Font configuration for different platforms."""

    @staticmethod
    def get_default_family() -> str:
        """Get the default font family for the current platform."""
        system = platform.system()
        if system == "Windows":
            return "Arial"  # Widely available on Windows
        elif system == "Darwin":  # macOS
            return "Helvetica"
        else:  # Linux (including WSL)
            return "DejaVu Sans"

    @staticmethod
    def get_monospace_family() -> str:
        """Get the monospace font family for the current platform."""
        system = platform.system()
        if system == "Windows":
            return "Consolas"
        elif system == "Darwin":
            return "Monaco"
        else:
            return "Monospace"

    # Font sizes
    SIZE_TITLE = 12
    SIZE_HEADING = 10
    SIZE_NORMAL = 9
    SIZE_SMALL = 8
    SIZE_LARGE_STAT = 16


class Spacing:
    """Spacing constants for consistent layout."""

    # Padding
    PAD_SMALL = 5
    PAD_MEDIUM = 10
    PAD_LARGE = 15
    PAD_XLARGE = 20

    # Widget sizes
    BUTTON_HEIGHT = 35
    BUTTON_WIDTH = 120
    SERVER_BUTTON_HEIGHT = 40
    SERVER_BUTTON_WIDTH = 150

    # Window dimensions
    WINDOW_MIN_WIDTH = 800
    WINDOW_MIN_HEIGHT = 600
    WINDOW_DEFAULT_WIDTH = 900
    WINDOW_DEFAULT_HEIGHT = 700


class Styles:
    """Pre-configured style dictionaries for common widgets."""

    @staticmethod
    def get_button_style() -> dict:
        """Style for standard buttons."""
        return {
            "font": (Fonts.get_default_family(), Fonts.SIZE_NORMAL),
            "relief": "raised",
            "bd": 2,
            "width": 12
        }

    @staticmethod
    def get_label_style() -> dict:
        """Style for standard labels."""
        return {
            "font": (Fonts.get_default_family(), Fonts.SIZE_NORMAL),
            "bg": Colours.BG_PRIMARY,
            "fg": Colours.TEXT_PRIMARY
        }

    @staticmethod
    def get_heading_style() -> dict:
        """Style for section headings."""
        return {
            "font": (Fonts.get_default_family(), Fonts.SIZE_HEADING, "bold"),
            "bg": Colours.BG_PRIMARY,
            "fg": Colours.TEXT_PRIMARY
        }

    @staticmethod
    def get_status_colour(latency_ms: float) -> str:
        """
        Get status colour based on ping latency.

        Args:
            latency_ms: Latency in milliseconds

        Returns:
            Hex colour code
        """
        if latency_ms < 0:
            return Colours.STATUS_FAILED
        elif latency_ms < 20:
            return Colours.STATUS_EXCELLENT
        elif latency_ms < 60:
            return Colours.STATUS_GOOD
        elif latency_ms < 110:
            return Colours.STATUS_FAIR
        else:
            return Colours.STATUS_POOR

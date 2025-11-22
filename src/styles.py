"""
UI styling constants and color schemes for the Ping Monitor application.
"""
import platform


class Colors:
    """Color palette for the application."""

    # Background colors - standard Windows gray
    BG_PRIMARY = "#F0F0F0"  # Standard Windows gray
    BG_SECONDARY = "#E0E0E0"
    BG_TERTIARY = "#D4D4D4"

    # Text colors
    TEXT_PRIMARY = "black"
    TEXT_SECONDARY = "#000000"
    TEXT_LIGHT = "#666666"

    # Status colors (for ping results) - more muted
    STATUS_EXCELLENT = "#008000"  # Dark green - < 50ms
    STATUS_GOOD = "#4C9900"       # Green - 50-100ms
    STATUS_FAIR = "#CC6600"       # Orange - 100-200ms
    STATUS_POOR = "#CC0000"       # Dark red - > 200ms
    STATUS_FAILED = "#666666"     # Gray - failed ping

    # Border colors
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
            return "MS Sans Serif"  # Classic Windows font
        elif system == "Darwin":  # macOS
            return "Helvetica"
        else:  # Linux
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
            "bg": Colors.BG_PRIMARY,
            "fg": Colors.TEXT_PRIMARY
        }

    @staticmethod
    def get_heading_style() -> dict:
        """Style for section headings."""
        return {
            "font": (Fonts.get_default_family(), Fonts.SIZE_HEADING, "bold"),
            "bg": Colors.BG_PRIMARY,
            "fg": Colors.TEXT_PRIMARY
        }

    @staticmethod
    def get_status_color(latency_ms: float) -> str:
        """
        Get status color based on ping latency.

        Args:
            latency_ms: Latency in milliseconds

        Returns:
            Hex color code
        """
        if latency_ms < 0:
            return Colors.STATUS_FAILED
        elif latency_ms < 50:
            return Colors.STATUS_EXCELLENT
        elif latency_ms < 100:
            return Colors.STATUS_GOOD
        elif latency_ms < 200:
            return Colors.STATUS_FAIR
        else:
            return Colors.STATUS_POOR

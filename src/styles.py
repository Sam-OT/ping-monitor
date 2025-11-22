"""
UI styling constants and color schemes for the Ping Monitor application.
"""
import platform


class Colors:
    """Color palette for the application."""

    # Background colors
    BG_PRIMARY = "#FFFFFF"
    BG_SECONDARY = "#F5F5F5"
    BG_TERTIARY = "#E8E8E8"

    # Accent colors
    ACCENT_BLUE = "#4A90E2"
    ACCENT_GREEN = "#5CB85C"
    ACCENT_ORANGE = "#F0AD4E"
    ACCENT_RED = "#D9534F"

    # Text colors
    TEXT_PRIMARY = "#333333"
    TEXT_SECONDARY = "#666666"
    TEXT_LIGHT = "#999999"

    # Status colors (for ping results)
    STATUS_EXCELLENT = "#27AE60"  # Green - < 50ms
    STATUS_GOOD = "#5CB85C"       # Light green - 50-100ms
    STATUS_FAIR = "#F39C12"       # Orange - 100-200ms
    STATUS_POOR = "#E74C3C"       # Red - > 200ms
    STATUS_FAILED = "#95A5A6"     # Gray - failed ping

    # Button colors
    BUTTON_PRIMARY = "#4A90E2"
    BUTTON_PRIMARY_HOVER = "#357ABD"
    BUTTON_SUCCESS = "#5CB85C"
    BUTTON_SUCCESS_HOVER = "#449D44"
    BUTTON_DANGER = "#D9534F"
    BUTTON_DANGER_HOVER = "#C9302C"

    # Border colors
    BORDER_LIGHT = "#DDDDDD"
    BORDER_MEDIUM = "#CCCCCC"
    BORDER_DARK = "#999999"


class Fonts:
    """Font configuration for different platforms."""

    @staticmethod
    def get_default_family() -> str:
        """Get the default font family for the current platform."""
        system = platform.system()
        if system == "Windows":
            return "Segoe UI"
        elif system == "Darwin":  # macOS
            return "SF Pro Text"
        else:  # Linux
            return "Ubuntu"

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
    SIZE_TITLE = 16
    SIZE_HEADING = 14
    SIZE_NORMAL = 11
    SIZE_SMALL = 9
    SIZE_LARGE_STAT = 24


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
    def get_server_button_style() -> dict:
        """Style for server selection buttons."""
        return {
            "font": (Fonts.get_default_family(), Fonts.SIZE_NORMAL),
            "bg": Colors.BUTTON_PRIMARY,
            "fg": "white",
            "activebackground": Colors.BUTTON_PRIMARY_HOVER,
            "activeforeground": "white",
            "relief": "flat",
            "cursor": "hand2",
            "height": 2,
            "width": 15
        }

    @staticmethod
    def get_add_button_style() -> dict:
        """Style for add server button."""
        return {
            "font": (Fonts.get_default_family(), Fonts.SIZE_NORMAL, "bold"),
            "bg": Colors.BUTTON_SUCCESS,
            "fg": "white",
            "activebackground": Colors.BUTTON_SUCCESS_HOVER,
            "activeforeground": "white",
            "relief": "flat",
            "cursor": "hand2",
            "width": 10
        }

    @staticmethod
    def get_remove_button_style() -> dict:
        """Style for remove server buttons."""
        return {
            "font": (Fonts.get_default_family(), Fonts.SIZE_SMALL, "bold"),
            "bg": Colors.BUTTON_DANGER,
            "fg": "white",
            "activebackground": Colors.BUTTON_DANGER_HOVER,
            "activeforeground": "white",
            "relief": "flat",
            "cursor": "hand2",
            "width": 2
        }

    @staticmethod
    def get_primary_button_style() -> dict:
        """Style for primary action buttons."""
        return {
            "font": (Fonts.get_default_family(), Fonts.SIZE_NORMAL, "bold"),
            "bg": Colors.BUTTON_PRIMARY,
            "fg": "white",
            "activebackground": Colors.BUTTON_PRIMARY_HOVER,
            "activeforeground": "white",
            "relief": "flat",
            "cursor": "hand2",
            "height": 2,
            "width": 20
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
    def get_stat_label_style() -> dict:
        """Style for statistics display labels."""
        return {
            "font": (Fonts.get_default_family(), Fonts.SIZE_LARGE_STAT, "bold"),
            "bg": Colors.BG_SECONDARY,
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

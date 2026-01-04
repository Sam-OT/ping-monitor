"""
Graph panel module for displaying ping results using matplotlib.
"""
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import List, Optional
from styles import Colours, Fonts, Styles


class GraphPanel:
    """Panel for displaying real-time ping graphs using matplotlib."""

    def __init__(self, parent: tk.Widget):
        """
        Initialize the graph panel.

        Args:
            parent: Parent tkinter widget
        """
        self.parent = parent
        self.canvas = None
        self.figure = None
        self.ax = None

        # Data storage
        self.ping_numbers = []
        self.latencies = []
        self.current_server = ""

        # Incremental update tracking
        self.line = None  # Line2D object for connecting line
        self.current_ylim_max = 100  # Track current y-axis maximum
        self.target_ping_count = 0  # Target number of pings

        self._setup_graph()

    def _setup_graph(self):
        """Set up the matplotlib figure and canvas."""
        # Create figure with white background (compact size to fit multiple graphs)
        self.figure = Figure(figsize=(3.5, 2.5), dpi=80, facecolor=Colours.BG_PRIMARY)
        self.ax = self.figure.add_subplot(111)

        # Use tight layout to prevent clipping
        self.figure.tight_layout(pad=1.0)

        # Style the plot
        self.ax.set_facecolor(Colours.BG_SECONDARY)
        self.ax.grid(True, linestyle='--', alpha=0.3, color=Colours.BORDER_MEDIUM)

        # Set x-axis for ping count display
        self.ax.set_xlabel('Ping Number', fontsize=Fonts.SIZE_NORMAL,
                          fontfamily=Fonts.get_default_family())
        self.ax.set_ylabel('Latency (ms)', fontsize=Fonts.SIZE_NORMAL,
                          fontfamily=Fonts.get_default_family())

        # Set spine colours
        for spine in self.ax.spines.values():
            spine.set_edgecolor(Colours.BORDER_MEDIUM)

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Initial empty plot
        self.clear()

    def clear(self):
        """Clear the graph and reset data."""
        self.ping_numbers = []
        self.latencies = []
        self.current_server = ""

        self.ax.clear()
        self.ax.set_facecolor(Colours.BG_SECONDARY)
        self.ax.grid(True, linestyle='--', alpha=0.3, color=Colours.BORDER_MEDIUM)
        self.ax.set_xlabel('Ping Number', fontsize=Fonts.SIZE_NORMAL,
                          fontfamily=Fonts.get_default_family())
        self.ax.set_ylabel('Latency (ms)', fontsize=Fonts.SIZE_NORMAL,
                          fontfamily=Fonts.get_default_family())
        self.ax.set_title('No data', fontsize=Fonts.SIZE_HEADING,
                         fontfamily=Fonts.get_default_family())

        # Set spine colours
        for spine in self.ax.spines.values():
            spine.set_edgecolor(Colours.BORDER_MEDIUM)

        self.canvas.draw_idle()

    def start_new_test(self, server_name: str, server_ip: str = "", target_ping_count: int = 60):
        """
        Start a new ping test, clearing previous data.

        Args:
            server_name: Name of the server being tested
            server_ip: IP address of the server
            target_ping_count: Number of pings to perform
        """
        # Clear data first
        self.ping_numbers = []
        self.latencies = []
        self.target_ping_count = target_ping_count

        # Title format: "Server Name: IP" - store for later use
        title = f'{server_name}: {server_ip}' if server_ip else server_name
        self.current_server = title  # Store AFTER clearing data

        # Clear and setup the axes (only once at start)
        self.ax.clear()
        self.ax.set_facecolor(Colours.BG_SECONDARY)
        self.ax.grid(True, linestyle='--', alpha=0.3, color=Colours.BORDER_MEDIUM)

        # Set initial x-axis range (will auto-scale as data comes in)
        self.ax.set_xlim(0, 10)

        # Set initial y-axis range
        self.current_ylim_max = 100
        self.ax.set_ylim(0, self.current_ylim_max)

        # Create persistent Line2D for connecting line
        self.line, = self.ax.plot([], [], color=Colours.BORDER_MEDIUM,
                                   linewidth=1.5, alpha=0.3, zorder=1)

        # Labels and styling
        self.ax.set_xlabel('Ping Number', fontsize=Fonts.SIZE_NORMAL,
                          fontfamily=Fonts.get_default_family())
        self.ax.set_ylabel('Latency (ms)', fontsize=Fonts.SIZE_NORMAL,
                          fontfamily=Fonts.get_default_family())

        # Set spine colours
        for spine in self.ax.spines.values():
            spine.set_edgecolor(Colours.BORDER_MEDIUM)

        # Set title
        self.ax.set_title(title,
                         fontsize=Fonts.SIZE_TITLE,
                         fontfamily=Fonts.get_default_family(),
                         color=Colours.TEXT_PRIMARY,
                         pad=10)

        # Adjust layout to prevent clipping
        self.figure.tight_layout(pad=1.0)
        self.canvas.draw_idle()

    def add_data_point(self, ping_number: int, latency: Optional[float]):
        """
        Add a new data point to the graph.

        Args:
            ping_number: Sequential ping number
            latency: Latency in milliseconds, or None if ping failed
        """
        self.ping_numbers.append(ping_number)

        # If ping failed, use -1 as a marker (won't be displayed)
        if latency is None:
            latency = 0  # Will show as 0 on graph

        self.latencies.append(latency)

        # Use incremental update instead of full redraw
        self._update_incremental()

    def _update_incremental(self):
        """Update graph incrementally without clearing."""
        if not self.ping_numbers:
            return

        # Separate valid pings from failed pings
        valid_pings = [(pn, lat) for pn, lat in zip(self.ping_numbers, self.latencies) if lat > 0]

        if valid_pings:
            valid_ping_numbers, valid_latencies = zip(*valid_pings)

            # Update the Line2D data (efficient, no redraw)
            self.line.set_data(valid_ping_numbers, valid_latencies)

            # Add only the LATEST scatter point
            latest_ping = self.ping_numbers[-1]
            latest_latency = self.latencies[-1]

            if latest_latency > 0:
                point_colour = Styles.get_status_colour(latest_latency)
                self.ax.scatter([latest_ping], [latest_latency],
                              color=point_colour, s=30, zorder=2)
            else:
                # Add failed ping marker
                self.ax.scatter([latest_ping], [0],
                              color=Colours.STATUS_FAILED, marker='x',
                              s=50, zorder=5)

            # Check if y-axis needs expansion
            max_current = max(valid_latencies)
            if max_current > self.current_ylim_max:
                self.current_ylim_max = max_current * 1.1
                self.ax.set_ylim(0, self.current_ylim_max)
        else:
            # All pings failed so far - add failed marker
            latest_ping = self.ping_numbers[-1]
            self.ax.scatter([latest_ping], [0],
                          color=Colours.STATUS_FAILED, marker='x',
                          s=50, zorder=5)

        # Auto-scale x-axis to show all pings
        max_ping = max(self.ping_numbers)
        self.ax.set_xlim(0, max(10, max_ping * 1.1))

        # Only redraw (non-blocking)
        self.canvas.draw_idle()

    def finalize_test(self):
        """Finalize the graph after test completion."""
        # Add legend if there were any failed pings
        if any(lat == 0 for lat in self.latencies):
            # Check if legend already exists, if not add it
            if not self.ax.get_legend():
                self.ax.scatter([], [], color=Colours.STATUS_FAILED,
                              marker='x', s=50, label='Failed')
                self.ax.legend(loc='upper right', fontsize=Fonts.SIZE_SMALL)
                self.canvas.draw_idle()

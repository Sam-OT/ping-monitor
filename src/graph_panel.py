"""
Graph panel module for displaying ping results using matplotlib.
"""
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import List, Optional
from styles import Colors, Fonts


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

        self._setup_graph()

    def _setup_graph(self):
        """Set up the matplotlib figure and canvas."""
        # Create figure with white background
        self.figure = Figure(figsize=(8, 4), dpi=100, facecolor=Colors.BG_PRIMARY)
        self.ax = self.figure.add_subplot(111)

        # Style the plot
        self.ax.set_facecolor(Colors.BG_SECONDARY)
        self.ax.grid(True, linestyle='--', alpha=0.3, color=Colors.BORDER_MEDIUM)
        self.ax.set_xlabel('Ping Number', fontsize=Fonts.SIZE_NORMAL,
                          fontfamily=Fonts.get_default_family())
        self.ax.set_ylabel('Latency (ms)', fontsize=Fonts.SIZE_NORMAL,
                          fontfamily=Fonts.get_default_family())

        # Set spine colors
        for spine in self.ax.spines.values():
            spine.set_edgecolor(Colors.BORDER_MEDIUM)

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
        self.ax.set_facecolor(Colors.BG_SECONDARY)
        self.ax.grid(True, linestyle='--', alpha=0.3, color=Colors.BORDER_MEDIUM)
        self.ax.set_xlabel('Ping Number', fontsize=Fonts.SIZE_NORMAL,
                          fontfamily=Fonts.get_default_family())
        self.ax.set_ylabel('Latency (ms)', fontsize=Fonts.SIZE_NORMAL,
                          fontfamily=Fonts.get_default_family())
        self.ax.set_title('No data', fontsize=Fonts.SIZE_HEADING,
                         fontfamily=Fonts.get_default_family())

        # Set spine colors
        for spine in self.ax.spines.values():
            spine.set_edgecolor(Colors.BORDER_MEDIUM)

        self.canvas.draw()

    def start_new_test(self, server_name: str, server_ip: str = ""):
        """
        Start a new ping test, clearing previous data.

        Args:
            server_name: Name of the server being tested
            server_ip: IP address of the server
        """
        self.current_server = server_name
        self.ping_numbers = []
        self.latencies = []
        self.clear()

        # Title format: "Server Name: IP"
        title = f'{server_name}: {server_ip}' if server_ip else server_name
        self.ax.set_title(title,
                         fontsize=Fonts.SIZE_HEADING,
                         fontfamily=Fonts.get_default_family(),
                         color=Colors.TEXT_PRIMARY)
        self.canvas.draw()

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
        self.update_graph()

    def update_graph(self):
        """Redraw the graph with current data."""
        if not self.ping_numbers:
            return

        self.ax.clear()

        # Filter out failed pings (0 values) for plotting
        valid_pings = [(pn, lat) for pn, lat in zip(self.ping_numbers, self.latencies) if lat > 0]

        if valid_pings:
            valid_ping_numbers, valid_latencies = zip(*valid_pings)

            # Determine line color based on average latency
            avg_latency = sum(valid_latencies) / len(valid_latencies)
            if avg_latency < 50:
                line_color = Colors.STATUS_EXCELLENT
            elif avg_latency < 100:
                line_color = Colors.STATUS_GOOD
            elif avg_latency < 200:
                line_color = Colors.STATUS_FAIR
            else:
                line_color = Colors.STATUS_POOR

            # Plot the line
            self.ax.plot(valid_ping_numbers, valid_latencies,
                        color=line_color, linewidth=2, marker='o',
                        markersize=4, label='Latency')

            # Add failed ping markers if any
            failed_pings = [pn for pn, lat in zip(self.ping_numbers, self.latencies) if lat == 0]
            if failed_pings:
                # Show failed pings at y=0
                self.ax.scatter(failed_pings, [0] * len(failed_pings),
                              color=Colors.STATUS_FAILED, marker='x',
                              s=50, label='Failed', zorder=5)

        # Style the plot
        self.ax.set_facecolor(Colors.BG_SECONDARY)
        self.ax.grid(True, linestyle='--', alpha=0.3, color=Colors.BORDER_MEDIUM)
        self.ax.set_xlabel('Ping Number', fontsize=Fonts.SIZE_NORMAL,
                          fontfamily=Fonts.get_default_family())
        self.ax.set_ylabel('Latency (ms)', fontsize=Fonts.SIZE_NORMAL,
                          fontfamily=Fonts.get_default_family())
        # Keep the same title (already set in start_new_test)

        # Set spine colors
        for spine in self.ax.spines.values():
            spine.set_edgecolor(Colors.BORDER_MEDIUM)

        # Add legend if there are failed pings
        if any(lat == 0 for lat in self.latencies):
            self.ax.legend(loc='upper right', fontsize=Fonts.SIZE_SMALL)

        # Set y-axis to start at 0
        if valid_pings:
            max_lat = max(valid_latencies)
            self.ax.set_ylim(0, max_lat * 1.1)  # 10% padding on top

        self.canvas.draw()

    def finalize_test(self):
        """Finalize the graph after test completion."""
        # Title is already set correctly in start_new_test, no need to change it
        pass

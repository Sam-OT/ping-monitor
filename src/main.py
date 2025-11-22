"""
Main GUI application for Ping Monitor.
"""
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import threading
from typing import Optional
from ping_service import PingService, PingResult
from storage import Storage, Server
from graph_panel import GraphPanel
from styles import Colors, Fonts, Spacing, Styles


class PingMonitorApp:
    """Main application window for Ping Monitor."""

    def __init__(self, root: tk.Tk):
        """
        Initialize the Ping Monitor application.

        Args:
            root: The root tkinter window
        """
        self.root = root
        self.root.title("Ping Monitor")
        self.root.geometry(f"{Spacing.WINDOW_DEFAULT_WIDTH}x{Spacing.WINDOW_DEFAULT_HEIGHT}")
        self.root.minsize(Spacing.WINDOW_MIN_WIDTH, Spacing.WINDOW_MIN_HEIGHT)
        self.root.configure(bg=Colors.BG_PRIMARY)

        # Initialize services
        self.ping_service = PingService()
        self.storage = Storage()

        # Load servers
        self.servers = self.storage.load_servers()

        # State
        self.current_test_running = False
        self.selected_duration = 60  # Default: 1 minute

        # UI Components
        self.server_buttons = {}
        self.stats_labels = {}
        self.graph_panel = None

        # Build UI
        self._build_ui()

    def _build_ui(self):
        """Build the complete user interface."""
        # Main container with padding
        main_frame = tk.Frame(self.root, bg=Colors.BG_PRIMARY)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=Spacing.PAD_LARGE, pady=Spacing.PAD_LARGE)

        # Top section: Server management
        self._build_server_section(main_frame)

        # Middle section: Duration selector
        self._build_duration_section(main_frame)

        # Statistics section
        self._build_stats_section(main_frame)

        # Graph section
        self._build_graph_section(main_frame)

        # Bottom section: Batch test button
        self._build_batch_section(main_frame)

        # Status bar
        self._build_status_bar(main_frame)

    def _build_server_section(self, parent):
        """Build the server selection and management section."""
        section_frame = tk.Frame(parent, bg=Colors.BG_PRIMARY)
        section_frame.pack(fill=tk.X, pady=(0, Spacing.PAD_MEDIUM))

        # Header with Add/Remove buttons
        header_frame = tk.Frame(section_frame, bg=Colors.BG_PRIMARY)
        header_frame.pack(fill=tk.X, pady=(0, Spacing.PAD_SMALL))

        tk.Label(header_frame, text="Servers:", **Styles.get_heading_style()).pack(side=tk.LEFT)

        btn_add = tk.Button(header_frame, text="+ Add Server",
                           command=self._add_server_dialog,
                           **Styles.get_add_button_style())
        btn_add.pack(side=tk.RIGHT, padx=Spacing.PAD_SMALL)

        # Scrollable server list
        self.server_list_frame = tk.Frame(section_frame, bg=Colors.BG_SECONDARY,
                                         relief=tk.SUNKEN, bd=1)
        self.server_list_frame.pack(fill=tk.BOTH, expand=False)

        # Canvas for scrolling
        canvas = tk.Canvas(self.server_list_frame, bg=Colors.BG_SECONDARY,
                          height=100, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.server_list_frame, orient=tk.HORIZONTAL,
                                 command=canvas.xview)
        self.scrollable_frame = tk.Frame(canvas, bg=Colors.BG_SECONDARY)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(xscrollcommand=scrollbar.set)

        canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Populate server buttons
        self._refresh_server_list()

    def _build_duration_section(self, parent):
        """Build the duration selection section."""
        section_frame = tk.Frame(parent, bg=Colors.BG_PRIMARY)
        section_frame.pack(fill=tk.X, pady=(0, Spacing.PAD_MEDIUM))

        tk.Label(section_frame, text="Test Duration:",
                **Styles.get_heading_style()).pack(side=tk.LEFT, padx=(0, Spacing.PAD_MEDIUM))

        # Radio buttons for duration
        self.duration_var = tk.IntVar(value=60)  # Default 1 minute

        durations = [
            ("10 seconds", 10),
            ("30 seconds", 30),
            ("1 minute", 60),
            ("5 minutes", 300)
        ]

        for text, value in durations:
            rb = tk.Radiobutton(section_frame, text=text, variable=self.duration_var,
                               value=value, bg=Colors.BG_PRIMARY, fg=Colors.TEXT_PRIMARY,
                               font=(Fonts.get_default_family(), Fonts.SIZE_NORMAL),
                               selectcolor=Colors.BG_SECONDARY,
                               activebackground=Colors.BG_PRIMARY,
                               cursor="hand2",
                               command=self._on_duration_changed)
            rb.pack(side=tk.LEFT, padx=Spacing.PAD_SMALL)

    def _build_stats_section(self, parent):
        """Build the statistics display section."""
        section_frame = tk.Frame(parent, bg=Colors.BG_SECONDARY, relief=tk.RIDGE, bd=2)
        section_frame.pack(fill=tk.X, pady=(0, Spacing.PAD_MEDIUM))

        tk.Label(section_frame, text="Statistics:", **Styles.get_heading_style()).pack(
            anchor=tk.W, padx=Spacing.PAD_MEDIUM, pady=(Spacing.PAD_SMALL, 0))

        # Grid for statistics
        stats_grid = tk.Frame(section_frame, bg=Colors.BG_SECONDARY)
        stats_grid.pack(fill=tk.X, padx=Spacing.PAD_LARGE, pady=Spacing.PAD_MEDIUM)

        # Create stat labels
        stats = [
            ("Mean:", "mean"),
            ("Min:", "min"),
            ("Max:", "max"),
            ("Std Dev:", "std_dev")
        ]

        for col, (label_text, key) in enumerate(stats):
            # Label
            tk.Label(stats_grid, text=label_text,
                    font=(Fonts.get_default_family(), Fonts.SIZE_NORMAL),
                    bg=Colors.BG_SECONDARY, fg=Colors.TEXT_SECONDARY).grid(
                row=0, column=col*2, sticky=tk.W, padx=(0, Spacing.PAD_SMALL))

            # Value
            value_label = tk.Label(stats_grid, text="--",
                                  font=(Fonts.get_default_family(), Fonts.SIZE_LARGE_STAT, "bold"),
                                  bg=Colors.BG_SECONDARY, fg=Colors.TEXT_PRIMARY)
            value_label.grid(row=0, column=col*2+1, sticky=tk.W, padx=(0, Spacing.PAD_LARGE))
            self.stats_labels[key] = value_label

    def _build_graph_section(self, parent):
        """Build the graph display section."""
        section_frame = tk.Frame(parent, bg=Colors.BG_PRIMARY, relief=tk.RIDGE, bd=2)
        section_frame.pack(fill=tk.BOTH, expand=True, pady=(0, Spacing.PAD_MEDIUM))

        self.graph_panel = GraphPanel(section_frame)

    def _build_batch_section(self, parent):
        """Build the batch test section."""
        section_frame = tk.Frame(parent, bg=Colors.BG_PRIMARY)
        section_frame.pack(fill=tk.X, pady=(0, Spacing.PAD_SMALL))

        self.batch_button = tk.Button(section_frame, text="Run All Servers",
                                     command=self._run_batch_test,
                                     **Styles.get_primary_button_style())
        self.batch_button.pack()

    def _build_status_bar(self, parent):
        """Build the status bar at the bottom."""
        self.status_bar = tk.Label(parent, text="Ready", bg=Colors.BG_TERTIARY,
                                  fg=Colors.TEXT_SECONDARY, anchor=tk.W,
                                  font=(Fonts.get_default_family(), Fonts.SIZE_SMALL),
                                  relief=tk.SUNKEN, bd=1)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def _refresh_server_list(self):
        """Refresh the server button list."""
        # Clear existing buttons
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.server_buttons.clear()

        # Create buttons for each server
        for i, server in enumerate(self.servers):
            # Container for server button and remove button
            btn_container = tk.Frame(self.scrollable_frame, bg=Colors.BG_SECONDARY)
            btn_container.pack(side=tk.LEFT, padx=Spacing.PAD_SMALL, pady=Spacing.PAD_MEDIUM)

            # Server button
            btn = tk.Button(btn_container, text=server.name,
                           command=lambda s=server: self._start_ping_test(s),
                           **Styles.get_server_button_style())
            btn.pack(side=tk.LEFT)

            # Remove button (small X)
            remove_btn = tk.Button(btn_container, text="×",
                                  command=lambda s=server: self._remove_server(s.name),
                                  **Styles.get_remove_button_style())
            remove_btn.pack(side=tk.LEFT, padx=(2, 0))

            self.server_buttons[server.name] = btn

    def _add_server_dialog(self):
        """Show dialog to add a new server."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Server")
        dialog.geometry("400x200")
        dialog.configure(bg=Colors.BG_PRIMARY)
        dialog.transient(self.root)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        # Form frame
        form_frame = tk.Frame(dialog, bg=Colors.BG_PRIMARY)
        form_frame.pack(expand=True, padx=Spacing.PAD_LARGE, pady=Spacing.PAD_LARGE)

        # Server name
        tk.Label(form_frame, text="Server Name:", **Styles.get_label_style()).grid(
            row=0, column=0, sticky=tk.W, pady=Spacing.PAD_SMALL)
        name_entry = tk.Entry(form_frame, font=(Fonts.get_default_family(), Fonts.SIZE_NORMAL),
                             width=30)
        name_entry.grid(row=0, column=1, pady=Spacing.PAD_SMALL)
        name_entry.focus()

        # IP Address
        tk.Label(form_frame, text="IP Address:", **Styles.get_label_style()).grid(
            row=1, column=0, sticky=tk.W, pady=Spacing.PAD_SMALL)
        ip_entry = tk.Entry(form_frame, font=(Fonts.get_default_family(), Fonts.SIZE_NORMAL),
                           width=30)
        ip_entry.grid(row=1, column=1, pady=Spacing.PAD_SMALL)

        # Status label
        status_label = tk.Label(form_frame, text="", bg=Colors.BG_PRIMARY,
                               fg=Colors.ACCENT_RED,
                               font=(Fonts.get_default_family(), Fonts.SIZE_SMALL))
        status_label.grid(row=2, column=0, columnspan=2, pady=Spacing.PAD_SMALL)

        def on_add():
            name = name_entry.get().strip()
            ip = ip_entry.get().strip()

            if not name or not ip:
                status_label.config(text="Please fill in all fields")
                return

            # Validate IP by pinging
            status_label.config(text="Validating IP address...", fg=Colors.TEXT_SECONDARY)
            dialog.update()

            if not self.ping_service.validate_ip(ip):
                status_label.config(text="Invalid or unreachable IP address", fg=Colors.ACCENT_RED)
                return

            # Add server
            self.servers, success, error = self.storage.add_server(self.servers, name, ip)

            if success:
                self._refresh_server_list()
                dialog.destroy()
                self._set_status(f"Added server: {name}")
            else:
                status_label.config(text=error, fg=Colors.ACCENT_RED)

        def on_cancel():
            dialog.destroy()

        # Buttons
        btn_frame = tk.Frame(form_frame, bg=Colors.BG_PRIMARY)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=Spacing.PAD_MEDIUM)

        tk.Button(btn_frame, text="Add", command=on_add,
                 bg=Colors.BUTTON_SUCCESS, fg="white",
                 font=(Fonts.get_default_family(), Fonts.SIZE_NORMAL),
                 cursor="hand2", width=10).pack(side=tk.LEFT, padx=Spacing.PAD_SMALL)

        tk.Button(btn_frame, text="Cancel", command=on_cancel,
                 bg=Colors.BUTTON_DANGER, fg="white",
                 font=(Fonts.get_default_family(), Fonts.SIZE_NORMAL),
                 cursor="hand2", width=10).pack(side=tk.LEFT, padx=Spacing.PAD_SMALL)

        # Bind Enter key
        dialog.bind('<Return>', lambda e: on_add())
        dialog.bind('<Escape>', lambda e: on_cancel())

    def _remove_server(self, name: str):
        """Remove a server after confirmation."""
        if messagebox.askyesno("Confirm Removal",
                              f"Are you sure you want to remove '{name}'?"):
            self.servers, success = self.storage.remove_server(self.servers, name)
            if success:
                self._refresh_server_list()
                self._set_status(f"Removed server: {name}")
            else:
                messagebox.showerror("Error", "Failed to remove server")

    def _on_duration_changed(self):
        """Handle duration selection change."""
        self.selected_duration = self.duration_var.get()

    def _start_ping_test(self, server: Server):
        """Start a ping test for a specific server."""
        if self.current_test_running:
            messagebox.showwarning("Test Running",
                                  "A test is already running. Please wait for it to complete.")
            return

        # Clear previous stats
        self._clear_stats()

        # Start graph
        self.graph_panel.start_new_test(server.name)

        # Run test in background thread
        self.current_test_running = True
        self._set_status(f"Testing {server.name}...")

        def run_test():
            def progress_callback(latency, current, total):
                # Update graph on main thread
                self.root.after(0, lambda: self.graph_panel.add_data_point(current, latency))

            result = self.ping_service.ping_continuous(
                server.name, server.ip, self.selected_duration, progress_callback
            )

            # Update UI with results on main thread
            self.root.after(0, lambda: self._display_results(result))

        thread = threading.Thread(target=run_test, daemon=True)
        thread.start()

    def _display_results(self, result: PingResult):
        """Display test results in the UI."""
        self.current_test_running = False
        self.graph_panel.finalize_test()

        if result.mean is not None:
            self.stats_labels["mean"].config(
                text=f"{result.mean:.2f} ms",
                fg=Styles.get_status_color(result.mean)
            )
            self.stats_labels["min"].config(
                text=f"{result.min:.2f} ms",
                fg=Styles.get_status_color(result.min)
            )
            self.stats_labels["max"].config(
                text=f"{result.max:.2f} ms",
                fg=Styles.get_status_color(result.max)
            )
            self.stats_labels["std_dev"].config(
                text=f"{result.std_dev:.2f} ms",
                fg=Colors.TEXT_PRIMARY
            )
            self._set_status(f"Test complete: {result.server_name} - Avg: {result.mean:.2f}ms")
        else:
            self._clear_stats()
            self._set_status(f"Test failed: {result.server_name}")
            messagebox.showerror("Test Failed", "All pings failed. Check the IP address.")

    def _clear_stats(self):
        """Clear all statistics displays."""
        for label in self.stats_labels.values():
            label.config(text="--", fg=Colors.TEXT_PRIMARY)

    def _run_batch_test(self):
        """Run ping tests on all servers and save results."""
        if self.current_test_running:
            messagebox.showwarning("Test Running",
                                  "A test is already running. Please wait for it to complete.")
            return

        if not self.servers:
            messagebox.showwarning("No Servers", "Please add at least one server first.")
            return

        # Confirm action
        if not messagebox.askyesno("Batch Test",
                                  f"Run {self.selected_duration}s ping test on all {len(self.servers)} servers?"):
            return

        self.current_test_running = True
        self._clear_stats()
        self.graph_panel.clear()
        self._set_status("Running batch test...")

        def run_batch():
            results = []
            for i, server in enumerate(self.servers):
                self.root.after(0, lambda s=server, idx=i:
                              self._set_status(f"Testing {idx+1}/{len(self.servers)}: {s.name}..."))

                result = self.ping_service.ping_continuous(
                    server.name, server.ip, self.selected_duration
                )
                results.append(str(result))

            # Save results
            success, filepath = self.storage.save_batch_results(results)

            # Update UI
            self.root.after(0, lambda: self._batch_complete(success, filepath))

        thread = threading.Thread(target=run_batch, daemon=True)
        thread.start()

    def _batch_complete(self, success: bool, filepath: str):
        """Handle batch test completion."""
        self.current_test_running = False

        if success:
            self._set_status(f"Batch test complete. Results saved.")
            messagebox.showinfo("Batch Test Complete",
                              f"Results saved to:\n{filepath}")
        else:
            self._set_status("Batch test failed")
            messagebox.showerror("Error", "Failed to save batch results")

    def _set_status(self, message: str):
        """Update the status bar."""
        self.status_bar.config(text=message)


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = PingMonitorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

"""
Main GUI application for Ping Monitor.
"""
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, filedialog
import threading
from typing import Optional
from ping_service import PingService, PingResult
from storage import Storage, Server
from graph_panel import GraphPanel
from styles import Colours, Fonts, Spacing, Styles


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
        self.root.configure(bg=Colours.BG_PRIMARY)

        # Initialize services
        self.ping_service = PingService()
        self.storage = Storage()

        # Load servers
        self.servers = self.storage.load_servers()

        # State
        self.current_test_running = False
        self.selected_duration = 60  # Default: 1 minute
        self.current_results = {}  # Store results: {server_name: PingResult}
        self.active_tests = 0  # Count of running tests
        self.cancel_event = threading.Event()  # Event to signal test cancellation

        # UI Components
        self.server_listbox = None
        self.stats_container = None  # Container for per-server stats
        self.stats_placeholder = None  # Placeholder label when no results
        self.graph_panels = {}  # Multiple graph panels for tiling
        self.graphs_container = None
        self.cancel_button = None

        # Build UI
        self._build_ui()

    def _build_ui(self):
        """Build the complete user interface."""
        # Main container with padding
        main_frame = tk.Frame(self.root, bg=Colours.BG_PRIMARY)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=Spacing.PAD_LARGE, pady=Spacing.PAD_LARGE)

        # Top section: Server management
        self._build_server_section(main_frame)

        # Middle section: Duration selector
        self._build_duration_section(main_frame)

        # Control section: Cancel button
        self._build_control_section(main_frame)

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
        section_frame = tk.Frame(parent, bg=Colours.BG_PRIMARY)
        section_frame.pack(fill=tk.BOTH, expand=True, pady=(0, Spacing.PAD_MEDIUM))

        # Header
        tk.Label(section_frame, text="Servers:", **Styles.get_heading_style()).pack(anchor=tk.W)

        # Container for listbox and buttons
        list_container = tk.Frame(section_frame, bg=Colours.BG_PRIMARY)
        list_container.pack(fill=tk.BOTH, expand=True, pady=Spacing.PAD_SMALL)

        # Listbox with scrollbar
        list_frame = tk.Frame(list_container, bg=Colours.BG_PRIMARY)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.server_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=(Fonts.get_default_family(), Fonts.SIZE_NORMAL),
            height=8,
            relief=tk.SUNKEN,
            bd=2,
            selectmode=tk.EXTENDED  # Allow multi-select
        )
        self.server_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.server_listbox.yview)

        # Buttons
        button_frame = tk.Frame(list_container, bg=Colours.BG_PRIMARY)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(Spacing.PAD_SMALL, 0))

        tk.Button(button_frame, text="Add",
                 command=self._add_server_dialog,
                 **Styles.get_button_style()).pack(pady=2)

        tk.Button(button_frame, text="Remove",
                 command=self._remove_selected_server,
                 **Styles.get_button_style()).pack(pady=2)

        tk.Button(button_frame, text="Import",
                 command=self._import_servers_dialog,
                 **Styles.get_button_style()).pack(pady=2)

        tk.Button(button_frame, text="Test",
                 command=self._test_selected_servers,
                 **Styles.get_button_style()).pack(pady=2)

        tk.Button(button_frame, text="Save Results",
                 command=self._save_current_results,
                 **Styles.get_button_style()).pack(pady=2)

        # Populate listbox
        self._refresh_server_list()

    def _build_duration_section(self, parent):
        """Build the duration selection section."""
        section_frame = tk.Frame(parent, bg=Colours.BG_PRIMARY)
        section_frame.pack(fill=tk.X, pady=(0, Spacing.PAD_MEDIUM))

        tk.Label(section_frame, text="Test Duration:",
                **Styles.get_heading_style()).pack(side=tk.LEFT, padx=(0, Spacing.PAD_MEDIUM))

        # Radio buttons for duration
        self.duration_var = tk.IntVar(value=5)  # Default 5 seconds
        self.use_custom_duration = tk.BooleanVar(value=False)

        durations = [
            ("5 seconds", 5),
            ("30 seconds", 30),
            ("1 minute", 60),
            ("5 minutes", 300)
        ]

        for text, value in durations:
            rb = tk.Radiobutton(section_frame, text=text, variable=self.duration_var,
                               value=value, bg=Colours.BG_PRIMARY, fg=Colours.TEXT_PRIMARY,
                               font=(Fonts.get_default_family(), Fonts.SIZE_NORMAL),
                               selectcolor=Colours.BG_SECONDARY,
                               activebackground=Colours.BG_PRIMARY,
                               cursor="hand2",
                               command=lambda: self.use_custom_duration.set(False))
            rb.pack(side=tk.LEFT, padx=Spacing.PAD_SMALL)

        # Custom duration entry
        tk.Label(section_frame, text="Custom (seconds):", bg=Colours.BG_PRIMARY,
                font=(Fonts.get_default_family(), Fonts.SIZE_NORMAL)).pack(
                    side=tk.LEFT, padx=(Spacing.PAD_MEDIUM, Spacing.PAD_SMALL))

        self.custom_duration_entry = tk.Entry(section_frame,
                                              font=(Fonts.get_default_family(), Fonts.SIZE_NORMAL),
                                              width=6)
        self.custom_duration_entry.pack(side=tk.LEFT, padx=Spacing.PAD_SMALL)
        self.custom_duration_entry.bind('<FocusIn>', lambda e: self.use_custom_duration.set(True))
        self.custom_duration_entry.bind('<Return>', lambda e: self._on_duration_changed())

    def _build_control_section(self, parent):
        """Build the control section with cancel button."""
        section_frame = tk.Frame(parent, bg=Colours.BG_PRIMARY)
        section_frame.pack(fill=tk.X, pady=(0, Spacing.PAD_MEDIUM))

        # Cancel button (centered)
        button_container = tk.Frame(section_frame, bg=Colours.BG_PRIMARY)
        button_container.pack()

        self.cancel_button = tk.Button(button_container, text="Cancel Test",
                                      command=self._cancel_test,
                                      state=tk.DISABLED,
                                      **Styles.get_button_style())
        self.cancel_button.pack(padx=Spacing.PAD_SMALL)

    def _build_stats_section(self, parent):
        """Build the statistics display section."""
        section_frame = tk.Frame(parent, bg=Colours.BG_PRIMARY, relief=tk.SUNKEN, bd=1)
        section_frame.pack(fill=tk.BOTH, expand=True, pady=(0, Spacing.PAD_MEDIUM))

        # Header
        header = tk.Frame(section_frame, bg=Colours.BG_SECONDARY, relief=tk.RAISED, bd=1)
        header.pack(fill=tk.X)
        tk.Label(header, text="Results", bg=Colours.BG_SECONDARY,
                font=(Fonts.get_default_family(), Fonts.SIZE_NORMAL, "bold")).pack(
                    anchor=tk.W, padx=Spacing.PAD_SMALL, pady=2)

        # Container for results (will hold per-server stats)
        self.stats_container = tk.Frame(section_frame, bg=Colours.BG_PRIMARY)
        self.stats_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Initial message
        self.stats_placeholder = tk.Label(self.stats_container, text="No test results yet",
                                         bg=Colours.BG_PRIMARY, fg=Colours.TEXT_LIGHT,
                                         font=(Fonts.get_default_family(), Fonts.SIZE_NORMAL))
        self.stats_placeholder.pack(pady=Spacing.PAD_MEDIUM)

    def _build_graph_section(self, parent):
        """Build the graph display section."""
        section_frame = tk.Frame(parent, bg=Colours.BG_PRIMARY, relief=tk.RIDGE, bd=2)
        section_frame.pack(fill=tk.BOTH, expand=True, pady=(0, Spacing.PAD_MEDIUM))

        # Container for multiple graph panels (tiled layout)
        self.graphs_container = tk.Frame(section_frame, bg=Colours.BG_PRIMARY)
        self.graphs_container.pack(fill=tk.BOTH, expand=True)

    def _build_batch_section(self, parent):
        """Build the batch test section."""
        section_frame = tk.Frame(parent, bg=Colours.BG_PRIMARY)
        section_frame.pack(fill=tk.X, pady=(0, Spacing.PAD_SMALL))

        # Container for batch button
        button_container = tk.Frame(section_frame, bg=Colours.BG_PRIMARY)
        button_container.pack()

        self.batch_button = tk.Button(button_container, text="Run All Servers",
                                     command=self._run_batch_test,
                                     **Styles.get_button_style())
        self.batch_button.pack(padx=Spacing.PAD_SMALL)

    def _build_status_bar(self, parent):
        """Build the status bar at the bottom."""
        self.status_bar = tk.Label(parent, text="Ready", bg=Colours.BG_TERTIARY,
                                  fg=Colours.TEXT_SECONDARY, anchor=tk.W,
                                  font=(Fonts.get_default_family(), Fonts.SIZE_SMALL),
                                  relief=tk.SUNKEN, bd=1)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def _refresh_server_list(self):
        """Refresh the server listbox."""
        self.server_listbox.delete(0, tk.END)
        for server in self.servers:
            self.server_listbox.insert(tk.END, f"{server.name} ({server.ip})")

    def _add_server_dialog(self):
        """Show dialog to add a new server."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Server")
        dialog.geometry("400x200")
        dialog.configure(bg=Colours.BG_PRIMARY)
        dialog.transient(self.root)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        # Form frame
        form_frame = tk.Frame(dialog, bg=Colours.BG_PRIMARY)
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
        status_label = tk.Label(form_frame, text="", bg=Colours.BG_PRIMARY,
                               fg=Colours.STATUS_POOR,
                               font=(Fonts.get_default_family(), Fonts.SIZE_SMALL))
        status_label.grid(row=2, column=0, columnspan=2, pady=Spacing.PAD_SMALL)

        def on_add():
            name = name_entry.get().strip()
            ip = ip_entry.get().strip()

            if not name or not ip:
                status_label.config(text="Please fill in all fields")
                return

            # Validate IP by pinging
            status_label.config(text="Validating IP address...", fg=Colours.TEXT_SECONDARY)
            dialog.update()

            if not self.ping_service.validate_ip(ip):
                status_label.config(text="Invalid or unreachable IP address", fg=Colours.STATUS_POOR)
                return

            # Add server
            self.servers, success, error = self.storage.add_server(self.servers, name, ip)

            if success:
                self._refresh_server_list()
                dialog.destroy()
                self._set_status(f"Added server: {name}")
            else:
                status_label.config(text=error, fg=Colours.STATUS_POOR)

        def on_cancel():
            dialog.destroy()

        # Buttons
        btn_frame = tk.Frame(form_frame, bg=Colours.BG_PRIMARY)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=Spacing.PAD_MEDIUM)

        tk.Button(btn_frame, text="Add", command=on_add,
                 **Styles.get_button_style()).pack(side=tk.LEFT, padx=Spacing.PAD_SMALL)

        tk.Button(btn_frame, text="Cancel", command=on_cancel,
                 **Styles.get_button_style()).pack(side=tk.LEFT, padx=Spacing.PAD_SMALL)

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

    def _remove_selected_server(self):
        """Remove the currently selected server(s)."""
        selection = self.server_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a server to remove")
            return

        # Get all selected servers
        selected_servers = [self.servers[i] for i in selection]

        # Confirm removal
        if len(selected_servers) == 1:
            confirm_msg = f"Are you sure you want to remove '{selected_servers[0].name}'?"
        else:
            confirm_msg = f"Are you sure you want to remove {len(selected_servers)} servers?"

        if not messagebox.askyesno("Confirm Removal", confirm_msg):
            return

        # Remove all selected servers
        for server in selected_servers:
            self.servers, success = self.storage.remove_server(self.servers, server.name)
            if not success:
                messagebox.showerror("Error", f"Failed to remove server: {server.name}")
                return

        self._refresh_server_list()
        self._set_status(f"Removed {len(selected_servers)} server(s)")

    def _import_servers_dialog(self):
        """Import servers from a text file."""
        # Open file dialog
        filepath = filedialog.askopenfilename(
            title="Import Server List",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            parent=self.root
        )

        if not filepath:
            return  # User cancelled

        # Read and parse the file
        added_count = 0
        skipped_count = 0
        failed_validation = []

        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()

            self._set_status(f"Importing servers...")

            for line_num, line in enumerate(lines, 1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue

                # Parse "Name: IP/hostname" format
                if ':' not in line:
                    skipped_count += 1
                    continue

                name, ip = line.split(':', 1)
                name = name.strip()
                ip = ip.strip()

                if not name or not ip:
                    skipped_count += 1
                    continue

                # Check if server already exists
                if any(s.name == name for s in self.servers):
                    skipped_count += 1
                    continue

                # Validate by pinging (show progress)
                self._set_status(f"Validating {name} ({ip})...")
                self.root.update()  # Update UI to show status
                if not self.ping_service.validate_ip(ip):
                    failed_validation.append(f"{name}: {ip}")
                    skipped_count += 1
                    continue

                # Add server
                self.servers, success, error = self.storage.add_server(self.servers, name, ip)
                if success:
                    added_count += 1
                else:
                    skipped_count += 1

            # Sort alphabetically
            self.servers = self.storage.sort_servers(self.servers)
            self._refresh_server_list()

            # Show summary
            summary = f"Import complete!\n\nAdded: {added_count} server(s)\nSkipped: {skipped_count} server(s)"
            if failed_validation:
                summary += f"\n\nFailed validation ({len(failed_validation)}):\n"
                summary += "\n".join(failed_validation[:5])  # Show first 5
                if len(failed_validation) > 5:
                    summary += f"\n... and {len(failed_validation) - 5} more"

            messagebox.showinfo("Import Results", summary)
            self._set_status(f"Imported {added_count} server(s)")

        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import file:\n{str(e)}")
            self._set_status("Import failed")

    def _test_selected_servers(self):
        """Test the currently selected server(s)."""
        selection = self.server_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select one or more servers to test")
            return

        if self.current_test_running:
            messagebox.showwarning("Test Running", "A test is already running. Please wait for it to complete.")
            return

        # Update duration (in case custom was entered)
        self._on_duration_changed()
        if self.selected_duration <= 0:
            return  # Invalid duration, warning already shown

        # Clear previous results and graphs
        self.current_results.clear()
        for widget in self.graphs_container.winfo_children():
            widget.destroy()
        self.graph_panels.clear()
        self._clear_stats()

        # Get selected servers
        selected_servers = [self.servers[i] for i in selection]

        # Calculate grid layout for graphs
        num_servers = len(selected_servers)
        cols = min(2, num_servers)  # Max 2 columns
        rows = (num_servers + cols - 1) // cols  # Ceiling division

        # Create graph panels in grid layout
        for idx, server in enumerate(selected_servers):
            row = idx // cols
            col = idx % cols

            graph_frame = tk.Frame(self.graphs_container, bg=Colours.BG_PRIMARY,
                                  relief=tk.RIDGE, bd=1)
            graph_frame.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)

            # Make grid cells expand evenly
            self.graphs_container.grid_rowconfigure(row, weight=1)
            self.graphs_container.grid_columnconfigure(col, weight=1)

            # Create graph panel for this server
            graph_panel = GraphPanel(graph_frame)
            self.graph_panels[server.name] = graph_panel

        # Start all tests simultaneously
        self.current_test_running = True
        self.active_tests = len(selected_servers)
        self.cancel_event.clear()  # Clear any previous cancel signal
        self.cancel_button.config(state=tk.NORMAL)  # Enable cancel button

        for server in selected_servers:
            self._start_ping_test(server)

    def _cancel_test(self):
        """Cancel the currently running test."""
        self.cancel_event.set()  # Signal all threads to stop
        self._set_status("Test cancelled by user")
        self.cancel_button.config(state=tk.DISABLED)  # Disable cancel button

    def _save_current_results(self):
        """Save current test results to a file."""
        if not self.current_results:
            messagebox.showwarning("No Results", "No test results to save. Run a test first.")
            return

        # Format results
        result_lines = []
        for server_name, result in self.current_results.items():
            result_lines.append(str(result))

        # Save to file
        success, filepath = self.storage.save_batch_results(result_lines)

        if success:
            messagebox.showinfo("Results Saved", f"Results saved to:\n{filepath}")
            self._set_status(f"Results saved to file")
        else:
            messagebox.showerror("Error", "Failed to save results")

    def _on_duration_changed(self):
        """Handle duration selection change."""
        if self.use_custom_duration.get():
            try:
                custom = int(self.custom_duration_entry.get())
                if custom > 0:
                    self.selected_duration = custom
                else:
                    messagebox.showwarning("Invalid Duration", "Duration must be positive")
            except ValueError:
                messagebox.showwarning("Invalid Duration", "Please enter a valid number")
        else:
            self.selected_duration = self.duration_var.get()

    def _start_ping_test(self, server: Server):
        """Start a ping test for a specific server."""
        # Get the graph panel for this server
        graph_panel = self.graph_panels.get(server.name)
        if not graph_panel:
            return

        # Start graph with duration
        graph_panel.start_new_test(server.name, server.ip, self.selected_duration)

        self._set_status(f"Testing {server.name}...")

        def run_test():
            def progress_callback(latency, current, total):
                # Update graph on main thread
                self.root.after(0, lambda l=latency, c=current:
                              graph_panel.add_data_point(c, l))

            result = self.ping_service.ping_continuous(
                server.name, server.ip, self.selected_duration, progress_callback, self.cancel_event
            )

            # Update UI with results on main thread
            self.root.after(0, lambda r=result: self._display_results(r))

        thread = threading.Thread(target=run_test, daemon=True)
        thread.start()

    def _display_results(self, result: PingResult):
        """Display test results in the UI."""
        # Store result
        self.current_results[result.server_name] = result

        # Finalize graph for this server
        graph_panel = self.graph_panels.get(result.server_name)
        if graph_panel:
            graph_panel.finalize_test()

        # Decrement active tests counter
        self.active_tests -= 1

        # Update stats when all tests are complete
        if self.active_tests == 0:
            self.current_test_running = False
            self.cancel_button.config(state=tk.DISABLED)  # Disable cancel button
            self._update_stats_display()
            self._set_status(f"Test complete ({len(self.current_results)} server(s))")

    def _update_stats_display(self):
        """Update the stats display with current results."""
        # Clear existing stats
        for widget in self.stats_container.winfo_children():
            widget.destroy()

        if not self.current_results:
            # Show placeholder
            self.stats_placeholder = tk.Label(self.stats_container, text="No test results yet",
                                             bg=Colours.BG_PRIMARY, fg=Colours.TEXT_LIGHT,
                                             font=(Fonts.get_default_family(), Fonts.SIZE_NORMAL))
            self.stats_placeholder.pack(pady=Spacing.PAD_MEDIUM)
            return

        # Create a read-only Text widget for selectable, monospace display
        text_widget = tk.Text(self.stats_container,
                             font=(Fonts.get_monospace_family(), Fonts.SIZE_NORMAL),
                             bg=Colours.BG_PRIMARY,
                             fg=Colours.TEXT_PRIMARY,
                             relief=tk.FLAT,
                             height=len(self.current_results) + 2,  # +2 for header and separator
                             wrap=tk.NONE,
                             cursor="arrow")
        text_widget.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Build header with left-aligned columns
        header = f"{'Server':<25} {'Mean':<13} {'Min':<13} {'Max':<13} {'Std Dev':<13}\n"
        text_widget.insert('1.0', header)
        text_widget.tag_add('header', '1.0', '1.end')
        text_widget.tag_config('header', font=(Fonts.get_monospace_family(), Fonts.SIZE_NORMAL, 'bold'))

        # Add separator line
        separator = "-" * 80 + "\n"
        text_widget.insert('end', separator)

        # Add results for each server
        line_num = 3
        for server_name, result in self.current_results.items():
            # Truncate server name if too long
            display_name = server_name[:24] if len(server_name) > 24 else server_name

            if result.mean is not None:
                # Format values with ms suffix, then align
                mean_str = f"{result.mean:.1f}ms"
                min_str = f"{result.min:.1f}ms"
                max_str = f"{result.max:.1f}ms"
                std_str = f"{result.std_dev:.1f}ms"
                line = f"{display_name:<25} {mean_str:<13} {min_str:<13} {max_str:<13} {std_str:<13}\n"
                text_widget.insert('end', line)

                # Colour-code the mean value
                mean_color = Styles.get_status_colour(result.mean)
                start_pos = f"{line_num}.26"
                end_pos = f"{line_num}.{26 + len(mean_str)}"
                text_widget.tag_add(f'mean_{line_num}', start_pos, end_pos)
                text_widget.tag_config(f'mean_{line_num}', foreground=mean_color)
            else:
                line = f"{display_name:<25} {'Failed':<13}\n"
                text_widget.insert('end', line)
                start_pos = f"{line_num}.26"
                end_pos = f"{line_num}.33"
                text_widget.tag_add(f'failed_{line_num}', start_pos, end_pos)
                text_widget.tag_config(f'failed_{line_num}', foreground=Colours.STATUS_FAILED)

            line_num += 1

        # Make read-only but allow selection
        text_widget.config(state='disabled')

    def _clear_stats(self):
        """Clear all statistics displays."""
        for widget in self.stats_container.winfo_children():
            widget.destroy()
        self.stats_placeholder = tk.Label(self.stats_container, text="No test results yet",
                                         bg=Colours.BG_PRIMARY, fg=Colours.TEXT_LIGHT,
                                         font=(Fonts.get_default_family(), Fonts.SIZE_NORMAL))
        self.stats_placeholder.pack(pady=Spacing.PAD_MEDIUM)

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
        # Clear graphs
        for widget in self.graphs_container.winfo_children():
            widget.destroy()
        self.graph_panels.clear()

        # Enable cancel button
        self.cancel_event.clear()
        self.cancel_button.config(state=tk.NORMAL)

        self._set_status("Running batch test...")

        def run_batch():
            results = []
            for i, server in enumerate(self.servers):
                # Check for cancellation
                if self.cancel_event.is_set():
                    self.root.after(0, lambda: self._set_status("Batch test cancelled"))
                    break

                self.root.after(0, lambda s=server, idx=i:
                              self._set_status(f"Testing {idx+1}/{len(self.servers)}: {s.name}..."))

                result = self.ping_service.ping_continuous(
                    server.name, server.ip, self.selected_duration,
                    cancel_event=self.cancel_event
                )
                results.append(str(result))

            # Save results
            success, filepath = self.storage.save_batch_results(results)

            # Update UI and hide cancel button
            self.root.after(0, lambda: self._batch_complete(success, filepath))

        thread = threading.Thread(target=run_batch, daemon=True)
        thread.start()

    def _batch_complete(self, success: bool, filepath: str):
        """Handle batch test completion."""
        self.current_test_running = False
        self.cancel_button.config(state=tk.DISABLED)  # Disable cancel button

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

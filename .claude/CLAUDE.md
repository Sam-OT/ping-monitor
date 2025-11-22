# Ping Monitor - Project Documentation

## Project Overview
A modern GUI application for monitoring network latency to multiple servers. Built with Python, tkinter, and matplotlib. Designed to be packaged as a standalone .exe with no Python installation required.

## Development Environment
- **Host OS**: Windows
- **Development**: WSL (Windows Subsystem for Linux)
- **Note**: Paths shown are Windows paths (e.g., `d:\Users\...`) but development is done in WSL environment

## Key Requirements (from user)
- **Visual appeal**: Modern, clean UI with good spacing and colours
- **User-friendly**: Easy to add/remove/select servers with custom names
- **Default duration**: 1 minute (with options for 10s, 30s, 1min, 5min)
- **Statistics**: Display mean, min, max, and standard deviation
- **Graphs**: Real-time visual charts of ping latency
- **Batch mode**: Test all servers and save to text file
- **Standalone packaging**: Single .exe file, no Python required

## Project Structure
```
ping-monitor/
├── .claude/                 # Claude documentation (this file)
├── src/
│   ├── main.py             # Main GUI application & entry point
│   ├── ping_service.py     # Cross-platform ping logic & statistics
│   ├── storage.py          # JSON-based server configuration
│   ├── graph_panel.py      # Matplotlib graph integration
│   └── styles.py           # UI styling constants (colours, fonts, spacing)
├── data/                   # Server configs (auto-created, gitignored)
├── results/                # Batch test outputs (auto-created, gitignored)
├── pyproject.toml          # Modern Python project config
├── build.spec              # PyInstaller configuration
├── README.md               # User documentation
└── .gitignore             # Git ignore (includes uv support)
```

## Technology Stack
- **Python**: 3.11+ required
- **GUI Framework**: tkinter (built-in, lightweight)
- **Graphing**: matplotlib with tkinter backend
- **Packaging**: PyInstaller for standalone .exe
- **Config Storage**: JSON files
- **Package Manager**: uv (modern, fast) or pip

## Architecture & Design Decisions

### Module Breakdown

**ping_service.py**
- Cross-platform ping using subprocess (Windows/Linux/Mac)
- Parses ping output with regex (different formats per OS)
- Windows: `ping -n 1 -w 1000 IP`
- Linux/Mac: `ping -c 1 -W 1 IP`
- Calculates statistics: mean, min, max, std dev
- Supports progress callbacks for real-time UI updates
- Validates IPs by attempting to ping them

**storage.py**
- JSON-based server storage in `data/servers.json`
- Auto-creates default servers (Google DNS, Cloudflare DNS)
- Server schema: `{"servers": [{"name": "...", "ip": "..."}]}`
- Batch results saved to `results/ping_results_YYYY-MM-DD_HH-MM-SS.txt`
- Prevents duplicate server names
- Auto-creates directories on first run

**styles.py**
- Centralized styling constants for consistent UI
- Colour scheme: Light theme with blue accents
- Status colours: Green (<50ms), Yellow (50-100ms), Orange (100-200ms), Red (>200ms)
- Platform-specific fonts: Segoe UI (Windows), SF Pro (Mac), Ubuntu (Linux)
- All spacing/padding constants defined here

**graph_panel.py**
- Embeds matplotlib Figure in tkinter Canvas
- Real-time graph updates during ping tests
- X-axis: Ping number, Y-axis: Latency (ms)
- Colour-coded lines based on average latency
- Shows failed pings as X markers at y=0
- Grid lines and clean styling

**main.py**
- Main application window (900x700 default, 800x600 minimum)
- Server management: scrollable horizontal list with add/remove
- Duration selector: Radio buttons for 10s/30s/1min/5min
- Statistics panel: Large numbers with colour coding
- Graph area: Embedded matplotlib panel
- Batch test button: Runs all servers sequentially
- Status bar: Shows current operation
- Threading: Ping tests run in background threads to prevent UI freezing
- Modal dialogs: Add server with IP validation

### Key Features

**Server Management**
- Click "+" to add server (validates IP by pinging)
- Each server button has "×" to remove
- Click server name to start ping test
- Confirmation dialog before removal
- Prevents duplicate names

**Ping Testing**
- Runs in background thread (non-blocking UI)
- Progress callbacks update graph in real-time
- Sends 1 ping per second for duration
- Handles timeouts gracefully
- Updates statistics after completion

**Statistics Display**
- Mean, Min, Max, Std Dev shown in large font
- Formatting: Mean/Min/Max as integers (e.g., "45ms"), Std Dev with one decimal (e.g., "12.5ms")
- Colour-coded by latency quality
- Updates in real-time during test
- Shows "--" when no data

**Save Results**
- "Save" button exports both TXT and PNG files with synchronized timestamps
- TXT file: Tabular format with statistics (mean, min, max, std dev)
- PNG file: Grid layout (2 columns) showing all graphs with color-coded data points
- Graph titles include mean latency: "SERVER_NAME: IP | Mean: XXms"
- Files saved to `results/` directory with timestamp format: `YYYY-MM-DD_HH-MM-SS`

**Batch Mode**
- Tests all servers sequentially
- Shows progress in status bar
- Can be saved using "Save" button after completion
- Format: ServerName with integer statistics

## Building & Running

### Development Setup

**Using uv (recommended):**
```bash
# Install uv (if not already installed)
pip install uv

# Install dependencies
uv sync

# Run the application
uv run python src/main.py
```

**Using pip:**
```bash
# Create virtual environment
python -m venv .venv

# Activate (Linux/WSL/macOS)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -e .

# Run application
python src/main.py
```

### Building Standalone Executable

**IMPORTANT**: PyInstaller creates executables for the platform it runs on:
- To build Windows `.exe` → must run on Windows (not WSL)
- To build Linux binary → must run on Linux/WSL
- To build macOS app → must run on macOS

**Build commands:**
```bash
# Install build dependencies
uv sync --extra dev

# Build executable
uv run pyinstaller build.spec
```

**Output locations:**
- Windows: `dist/PingMonitor.exe`
- Linux/macOS: `dist/PingMonitor` (binary)

**WSL Users**: If developing in WSL but need Windows `.exe`:
1. Exit WSL
2. Open Windows PowerShell/CMD in project directory
3. Run: `uv sync --extra dev`
4. Run: `uv run pyinstaller build.spec`

### PyInstaller Configuration Notes
- All paths in `build.spec` use Unix-style forward slashes (cross-platform compatible)
- `--onefile`: Single executable
- `--windowed`: No console window (GUI mode)
- Hidden imports: matplotlib.backends.backend_tkagg
- Excludes: pytest, setuptools (reduces size)
- UPX compression enabled

## Testing Checklist
- [ ] Add server with valid IP (should validate and add)
- [ ] Add server with invalid IP (should show error)
- [ ] Add duplicate server name (should reject)
- [ ] Remove server (should show confirmation)
- [ ] Run 10s ping test (should complete in ~10s)
- [ ] Run 1min ping test (should show real-time graph)
- [ ] Check statistics are correct
- [ ] Graph updates in real-time
- [ ] Batch test all servers (should save file)
- [ ] Test with unreachable IP (should handle gracefully)
- [ ] Verify .exe works on clean Windows machine

## Common Issues & Solutions

**Issue**: Ping validation fails
- **Cause**: Firewall blocking ICMP
- **Solution**: Check Windows Firewall, allow ping

**Issue**: Graph doesn't update
- **Cause**: Threading issue with tkinter
- **Solution**: Use `root.after()` to update on main thread

**Issue**: .exe is too large
- **Cause**: matplotlib includes many backends
- **Solution**: Already optimized with excludes in build.spec

**Issue**: Can't ping certain servers
- **Cause**: Different ping output formats
- **Solution**: Regex patterns handle Windows/Linux/Mac

**Issue**: Stats show "--" after test
- **Cause**: All pings failed
- **Solution**: Check IP address, network connectivity

## Future Enhancement Ideas
- [ ] Historical data tracking over time
- [ ] Alerts/notifications for high latency
- [ ] Custom ping intervals (currently 1s fixed)
- [ ] Dark mode theme
- [ ] Save/load multiple server profiles
- [ ] Packet loss percentage display
- [ ] Traceroute integration
- [ ] System tray icon
- [ ] Auto-run at startup option

## Dependencies (from pyproject.toml)
```toml
dependencies = [
    "matplotlib>=3.8.0",
    "numpy>=1.24.0",  # Required by matplotlib
]

[project.optional-dependencies]
dev = [
    "pyinstaller>=6.0.0",
]
```

## Git Info
- **Branch**: main
- **Initial commit**: ff163e8
- **gitignored**: data/, results/, venv/, .venv/, build/, dist/, uv.lock

## Design Philosophy
- **Simplicity**: Single-purpose, does one thing well
- **User-friendly**: No technical knowledge required
- **Visual**: Clean, modern UI with colour coding
- **Fast**: uv for quick dependency management
- **Portable**: Standalone .exe, no dependencies
- **Cross-platform code**: Works on Windows/Linux/Mac (source)

## Notes
- Default servers: Google DNS (8.8.8.8), Cloudflare DNS (1.1.1.1)
- Default duration: 60 seconds (1 minute)
- Ping interval: 1 second (hardcoded)
- Timeout per ping: 2 seconds
- Storage format: JSON (human-readable, easy to edit)
- Threading: daemon threads prevent hanging on close
- UI updates: Always use `root.after()` from worker threads

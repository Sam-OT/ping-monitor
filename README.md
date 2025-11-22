# Ping Monitor

A modern, user-friendly GUI application for monitoring network latency to multiple servers.

## Features

- Visual Server Management
- Configurable Ping Tests
- Real-time Statistics
- Live Graphs
- Batch Testing
- Standalone Executable

## Installation

### For Users
Download and run `PingMonitor.exe`

### For Developers
1. Install uv: `pip install uv`
2. Clone this repository
3. Install dependencies: `uv sync`
4. Run: `uv run python src/main.py`

If using traditional `pip`, install dependencies with `pip install -e .`

## Usage

Click "+" to add servers. Click a server name to run a ping test. Select duration (default: 1 minute). View statistics and real-time graphs. Use "Run All Servers" for batch testing.

## Building from Source

### Development (Linux/WSL/macOS)

```bash
# Install dependencies
uv sync

# Run the application
uv run python src/main.py
```

### Building Executable

**Important**: PyInstaller creates executables for the platform it runs on. To create a Windows `.exe`, you must build on Windows. To create a Linux binary, build on Linux.

#### On Windows (PowerShell/CMD)

```powershell
# Install build dependencies
uv sync --extra dev

# Build executable
uv run pyinstaller build.spec
```

#### On Linux/WSL/macOS

```bash
# Install build dependencies
uv sync --extra dev

# Build executable (creates platform-specific binary)
uv run pyinstaller build.spec
```

The executable will be created in the `dist/` directory.

**WSL Users**: If developing in WSL but need a Windows `.exe`, you must run PyInstaller from Windows PowerShell/CMD, not from within WSL.

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

```bash
uv sync --extra dev
uv run pyinstaller build.spec
```

The executable will be created in the `dist/` directory.

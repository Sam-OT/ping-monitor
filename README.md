# Ping Monitor

A modern, user-friendly GUI application for monitoring network latency to multiple servers.

## Features

- **Visual Server Management**: Easy-to-use interface for adding, removing, and selecting servers with custom names
- **Configurable Ping Tests**: Choose test duration (10s, 30s, 1min, 5min) with 1-minute default
- **Real-time Statistics**: View mean, min, max, and standard deviation of ping times
- **Live Graphs**: Watch ping latency in real-time with clean, visual charts
- **Batch Testing**: Run tests on all servers at once and save results to a text file
- **Standalone Executable**: No Python installation required - packaged as a single .exe file

## Installation

### For Users
Simply download and run the `PingMonitor.exe` file. No installation or dependencies required!

### For Developers

#### Using uv (Recommended - Fast!)
1. Install uv: `pip install uv` or visit [uv installation guide](https://github.com/astral-sh/uv)
2. Clone this repository
3. Install dependencies: `uv sync`
4. Run the application: `uv run python src/main.py`

#### Using traditional pip
1. Clone this repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Mac/Linux: `source .venv/bin/activate`
4. Install dependencies: `pip install -e .`
5. Run the application: `python src/main.py`

## Usage

1. **Add Servers**: Click the "+" button to add a server with a custom name and IP address
2. **Select Server**: Click on any server button to run a ping test
3. **Choose Duration**: Select how long to run the test (default: 1 minute)
4. **View Results**: See statistics and a real-time graph of ping times
5. **Batch Test**: Click "Run All Servers" to test all servers and save results to a file
6. **Remove Servers**: Click the "×" button on any server to remove it

## Building from Source

To build the standalone executable:

#### Using uv (Recommended)
```bash
uv sync --extra dev
uv run pyinstaller build.spec
```

#### Using pip
```bash
pip install pyinstaller
pyinstaller build.spec
```

The executable will be created in the `dist/` directory.

## Requirements

- Python 3.11+
- matplotlib
- numpy
- tkinter (usually included with Python)

## License

MIT License

## Author

Created with Python, tkinter, and matplotlib.

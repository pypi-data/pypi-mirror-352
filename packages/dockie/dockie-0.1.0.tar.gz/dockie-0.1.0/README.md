# Dockie - Docker TUI

A Terminal User Interface (TUI) for Docker management built with Textual.

## Features

### ✅ Containers Management

- **View all containers**: Shows running and stopped containers in a clean table format
- **Real-time status**: Color-coded status indicators (green for running, red for exited, yellow for other states)
- **Container uptime**: Shows how long running containers have been up (e.g., "2d 14h 30m")
- **Fuzzy search**: Filter containers by name, image, or status with intelligent fuzzy matching
- **Container operations**:
  - Restart containers
  - **Full-screen live log viewer**: View container logs using native Docker commands with real-time tailing
  - Refresh container list
- **Advanced log viewer**:
  - **Native Docker integration**: Uses `docker logs -f` for real-time log following
  - **Full-screen display**: Logs take up the entire screen except for header/footer
  - **Raw Docker output**: Displays logs exactly as `docker logs -f -n 10000` would show
  - **Interactive scrolling**: Full scroll support with keyboard navigation
  - **Auto-scrolling**: Automatically follows new logs, but can be disabled by scrolling up
  - **Memory efficient**: Keeps only the last 10000 log lines in memory
  - **Live updates**: Real-time log streaming
- **Keyboard shortcuts**:
  - `Escape` - Go back to main menu
  - `r` or `Ctrl+R` - Refresh container list
  - `Tab` - Toggle focus between search and table
  - `Ctrl+L` - Show logs for selected container
  - `Ctrl+A` - Toggle auto-refresh
  - `Ctrl+E` - Toggle show/hide exited containers
  - In log viewer: 
    - `Escape` or `Q` - Close logs
    - `Ctrl+C` - Stop following logs (but keep viewer open)
    - `R` - Restart log following

### 🚧 Planned Features

- Images management
- Networks management
- Volumes management
- Container statistics and monitoring

## Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd dockie-py
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```
   Or with pip:
   ```bash
   pip install -e .
   ```

## Usage

1. **Make sure Docker is running** on your system

2. **Run the application**:

   ```bash
   python main.py
   ```

   Or if installed:

   ```bash
   dockie
   ```

3. **Navigate the interface**:
   - Use the main menu to select "Containers"
   - Use arrow keys to navigate the container table
   - View container information including ID, name, image, status, creation time, uptime, and ports
   - Use the search box to filter containers
   - Select a container and use the action buttons: Restart, Logs, or Refresh

## Requirements

- Python 3.12+
- Docker installed and running
- Terminal with support for mouse and keyboard input

## Dependencies

- **textual**: Modern TUI framework
- **docker**: Python Docker SDK
- **fuzzywuzzy**: Fuzzy string matching for search
- **python-levenshtein**: Fast string matching algorithms

## Screenshots

The application provides:

- A clean main menu with navigation options
- A detailed containers view with real-time information
- Intuitive search and filtering capabilities
- Color-coded status indicators for quick visual feedback

## Development

To contribute to the project:

1. Install development dependencies:

   ```bash
   uv sync --dev
   ```

2. Run tests:

   ```bash
   pytest
   ```

3. Format code:
   ```bash
   black .
   ruff check .
   ```

## License

MIT License - see LICENSE file for details.

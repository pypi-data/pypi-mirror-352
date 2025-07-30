"""Container management functionality for Dockie."""

import docker
from dockie import __version__
from docker.errors import DockerException
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Button,
    DataTable,
    Input,
    Label,
    Footer,
    Header,
    RichLog,
)
from textual.screen import Screen
from textual.binding import Binding
from textual.coordinate import Coordinate
from rich.text import Text
from textual.events import Key

from fuzzywuzzy import fuzz
from typing import Dict, Any, Optional
import datetime
import asyncio
import os


class LogViewerScreen(Screen):
    """Enhanced full-screen viewer for live container logs using Textual Log widget."""

    CSS = """
    LogViewerScreen {
        layout: vertical;
    }

    #log-container {
        width: 100%;
        height: 100%;
    }

    #log-widget {
        height: 1fr;
        width: 100%;
        background: #000000;
        color: #ffffff;
        border: none;
        scrollbar-background: #333333;
        scrollbar-color: #666666;
        scrollbar-corner-color: #333333;
    }

    #log-info {
        height: 3;
        width: 100%;
        background: #1e1e1e;
        color: #ffffff;
        padding: 1;
        margin: 0;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("r", "refresh", "Refresh"),
        Binding("ctrl+r", "refresh", "Refresh"),
        Binding("ctrl+l", "clear_logs", "Clear Logs"),
        Binding("home", "scroll_home", "Scroll to Top"),
        Binding("end", "scroll_end", "Scroll to Bottom"),
    ]

    def __init__(self, container_name: str, container_id: str):
        super().__init__()
        self.container_name = container_name
        self.container_id = container_id
        self.log_process = None
        self._running = False

    def compose(self) -> ComposeResult:
        """Create the log viewer layout."""
        yield Header(show_clock=True)
        yield Container(
            Label(f"📋 Docker Logs - {self.container_name} (0 lines)", id="log-info"),
            RichLog(
                highlight=True,
                auto_scroll=True,
                max_lines=50000,
                id="log-widget",
                wrap=True,
            ),
            id="log-container",
        )
        yield Footer()

    async def on_mount(self) -> None:
        """Start following logs when the screen mounts."""
        # Update the header
        header = self.query_one(Header)
        header.tall = False

        # Start following logs
        await self._restart_logs()

    async def start_following_logs(self):
        """Start following Docker logs."""
        if self._running:
            return

        try:
            # Start docker logs process
            cmd = [
                "docker",
                "logs",
                "-f",
                "-n",
                "10000",  # Show last 10000 lines initially
                self.container_id,
            ]

            self.log_process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env=dict(os.environ, TERM="xterm-256color"),
            )

            self._running = True
            # Start reading output
            asyncio.create_task(self._read_output())

        except Exception as e:
            # Show error in log
            log_widget = self.query_one("#log-widget", RichLog)
            log_widget.write(f"Error starting logs: {str(e)}")

    async def _read_output(self):
        """Read output from docker logs process and write to Log widget."""
        if not self.log_process or not self.log_process.stdout:
            return

        log_widget = self.query_one("#log-widget", RichLog)
        buffer = ""

        try:
            while self._running and self.log_process:
                # Read data in chunks
                data = await self.log_process.stdout.read(8192)
                if not data:
                    break

                # Decode and add to buffer
                try:
                    text = data.decode("utf-8", errors="replace")
                    buffer += text

                    # Process complete lines
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.rstrip()
                        if line:  # Only add non-empty lines
                            log_widget.write(line)

                            # Update line count in info bar
                            self._update_line_count()

                except Exception:
                    # If decoding fails, continue
                    continue

        except Exception:
            # Process ended or error occurred
            pass
        finally:
            # Add any remaining buffer content
            if buffer.strip():
                log_widget.write(buffer.rstrip())
                self._update_line_count()
            self._running = False

    def _update_line_count(self):
        """Update the line count in the info bar."""
        log_widget = self.query_one("#log-widget", RichLog)
        line_count = len(log_widget.lines)
        log_info = self.query_one("#log-info", Label)
        log_info.update(
            f"📋 Docker Logs - {self.container_name} ({line_count:,} lines)"
        )

    async def stop_following_logs(self):
        """Stop following logs."""
        self._running = False
        if self.log_process:
            try:
                self.log_process.terminate()
                await self.log_process.wait()
            except Exception:
                pass
            self.log_process = None

    def action_close(self) -> None:
        """Close the log viewer."""
        asyncio.create_task(self._cleanup_and_close())

    async def _cleanup_and_close(self):
        """Clean up resources and close."""
        await self.stop_following_logs()
        self.app.pop_screen()

    def action_refresh(self) -> None:
        """Restart the log following."""
        asyncio.create_task(self._restart_logs())

    async def _restart_logs(self):
        """Restart log following."""
        await self.stop_following_logs()

        # Clear existing logs and restart
        log_widget = self.query_one("#log-widget", RichLog)
        log_widget.clear()

        await self.start_following_logs()

        # Show restart message
        log_info = self.query_one("#log-info", Label)
        log_info.update(f"📋 Docker Logs - {self.container_name} (Refreshed)")

    def action_clear_logs(self) -> None:
        """Clear the log display."""
        log_widget = self.query_one("#log-widget", RichLog)
        log_widget.clear()
        log_info = self.query_one("#log-info", Label)
        log_info.update(f"📋 Docker Logs - {self.container_name} (0 lines)")

    def action_scroll_home(self) -> None:
        """Scroll to the top of logs."""
        log_widget = self.query_one("#log-widget", RichLog)
        log_widget.scroll_home(animate=True)

    def action_scroll_end(self) -> None:
        """Scroll to the bottom of logs."""
        log_widget = self.query_one("#log-widget", RichLog)
        log_widget.scroll_end(animate=True)


class ContainerScreen(Screen):
    """Screen for managing Docker containers."""

    CSS = """
    ContainerScreen {
        layout: vertical;
    }

    .header-section {
        height: auto;
        margin: 1;
    }

    .search-section {
        height: 3;
        margin: 1;
    }

    .table-section {
        height: 1fr;
        margin: 1;
    }

    .controls-section {
        height: 3;
        margin: 1;
        width: 100%;
        align: center middle;
        content-align: center middle;
    }

    .control-button {
        width: 1fr;
        max-width: 20%;
    }

    Input {
        width: 100%;
    }

    DataTable {
        height: 1fr;
        width: 100%;
    }

    Button {
        margin: 0 1;
        height: 3;
    }

    """
    column_names = ["Status", "Name", "ID", "Created", "Uptime", "Ports", "Image"]

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("escape", "back", "Back"),
        Binding("r", "refresh", "Refresh"),
        Binding("ctrl+l", "logs_selected", "Show Logs"),
        Binding("enter", "logs_selected", "Show Logs"),
        Binding("tab", "focus_toggle", "Focus Toggle"),
        Binding("ctrl+r", "restart_selected", "Restart Selected"),
        Binding("ctrl+a", "toggle_auto_refresh", "Toggle Auto-refresh"),
        Binding("ctrl+e", "toggle_exited", "Toggle Show/Hide Exited"),
    ]

    def __init__(self):
        super().__init__()
        self.docker_client = None
        self.all_containers = []
        self.filtered_containers = []
        self.show_exited = False  # Default to hiding exited containers
        self.auto_refresh_enabled = True
        self.auto_refresh_timer = None
        self.uptime_refresh_timer = None
        self.last_full_refresh = None

    def compose(self) -> ComposeResult:
        """Create the container screen layout."""
        yield Container(
            # Header
            Vertical(
                Label(f"🐳 Dockie v2 {__version__}", classes="title"),
                classes="header-section",
            ),
            # Search
            Vertical(
                Label("🔍 Search containers:"),
                Input(
                    placeholder="Filter containers by name, image, or status...",
                    id="search-input",
                ),
                classes="search-section",
            ),
            # Container table
            Vertical(
                DataTable(id="containers-table"),
                classes="table-section",
            ),
            # Controls
            Horizontal(
                Button(
                    "🔄 Restart",
                    id="restart-btn",
                    variant="warning",
                    classes="control-button",
                ),
                Button(
                    "📋 Logs",
                    id="logs-btn",
                    variant="default",
                    classes="control-button",
                ),
                Button(
                    "🔁 Refresh",
                    id="refresh-btn",
                    variant="primary",
                    classes="control-button",
                ),
                classes="controls-section",
            ),
            id="container-screen",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the screen when mounted."""
        self.setup_docker_client()
        self.setup_table()
        self.refresh_containers()
        self.start_auto_refresh()

    def setup_docker_client(self) -> None:
        """Initialize Docker client."""
        try:
            self.docker_client = docker.from_env()
            # Test connection
            self.docker_client.ping()
        except DockerException as e:
            self.notify(f"Failed to connect to Docker: {e}", severity="error")
            self.docker_client = None

    def setup_table(self) -> None:
        """Setup the containers table."""
        table = self.query_one("#containers-table", DataTable)
        # Add columns first without widths
        table.add_columns("Status", "Name", "ID", "Created", "Uptime", "Ports", "Image")
        table.cursor_type = "row"

    def refresh_containers(self) -> None:
        """Refresh container list from Docker."""
        if not self.docker_client:
            self.notify("Docker client not available", severity="error")
            return

        try:
            # Get all containers (including stopped ones)
            containers = self.docker_client.containers.list(all=True)
            self.all_containers = []

            for container in containers:
                # Format creation time
                created = container.attrs["Created"]
                created_dt = datetime.datetime.fromisoformat(
                    created.replace("Z", "+00:00")
                )
                created_str = created_dt.strftime("%Y-%m-%d %H:%M")

                # Calculate uptime for running containers
                uptime_str = ""
                if container.status == "running":
                    started_at = container.attrs.get("State", {}).get("StartedAt")
                    if started_at:
                        started_dt = datetime.datetime.fromisoformat(
                            started_at.replace("Z", "+00:00")
                        )
                        uptime_delta = (
                            datetime.datetime.now(datetime.timezone.utc) - started_dt
                        )

                        # Format uptime in a human-readable way
                        days = uptime_delta.days
                        hours, remainder = divmod(uptime_delta.seconds, 3600)
                        minutes, seconds = divmod(remainder, 60)

                        if days > 0:
                            # More than 1 day: show dd hh mm (no seconds)
                            uptime_str = f"{days}d {hours}h {minutes}m"
                        else:
                            # Less than 1 day: show hh mm ss
                            uptime_str = f"{hours}h {minutes}m {seconds}s"
                else:
                    uptime_str = "-"

                # Format ports
                ports = container.attrs.get("NetworkSettings", {}).get("Ports", {})
                port_list = []
                for internal_port, external in ports.items():
                    if external:
                        for ext in external:
                            port_list.append(f"{ext['HostPort']}:{internal_port}")
                    else:
                        port_list.append(internal_port)
                ports_str = ", ".join(port_list) if port_list else ""

                container_info = {
                    "id": container.short_id,
                    "name": container.name,
                    "image": container.image.tags[0]
                    if container.image.tags
                    else container.image.short_id,
                    "status": container.status,
                    "created": created_str,
                    "uptime": uptime_str,
                    "ports": ports_str,
                    "container_obj": container,
                }
                self.all_containers.append(container_info)

            self.apply_filters()

        except DockerException as e:
            self.notify(f"Failed to load containers: {e}", severity="error")

    def apply_filters(self) -> None:
        """Apply both status and search filters to containers."""
        # First filter by exited status if needed
        if self.show_exited:
            containers_to_filter = self.all_containers.copy()
        else:
            containers_to_filter = [
                c for c in self.all_containers if c["status"] != "exited"
            ]

        # Then apply search filter
        search_input = self.query_one("#search-input", Input)
        search_term = search_input.value if hasattr(search_input, "value") else ""

        if not search_term.strip():
            self.filtered_containers = containers_to_filter
        else:
            self.filtered_containers = []
            search_term_lower = search_term.lower()

            for container in containers_to_filter:
                # Check if search term matches any field
                searchable_text = f"{container['name']} {container['image']} {container['status']}".lower()

                # Use fuzzy matching with a threshold
                if (
                    search_term_lower in searchable_text
                    or fuzz.partial_ratio(search_term_lower, searchable_text) > 85
                ):
                    self.filtered_containers.append(container)

        self.update_table()

    def update_table(self) -> None:
        """Update the table with filtered containers."""
        table = self.query_one("#containers-table", DataTable)
        table.clear()

        for id, container in enumerate(self.filtered_containers, start=1):
            # Color status based on container state
            status = container["status"]
            if status == "running":
                status_display = f"[green]{status}[/green]"
            elif status == "exited":
                status_display = f"[red]{status}[/red]"
            else:
                status_display = f"[yellow]{status}[/yellow]"

            label = Text(str(id), style="italic")
            table.add_row(
                status_display,
                container["name"],
                container["id"],
                container["created"],
                container["uptime"],
                container["ports"],
                container["image"],
                label=label,
            )

    def filter_containers(self) -> None:
        """Filter containers based on search term using fuzzy matching."""
        self.apply_filters()

    def get_selected_container(self) -> Optional[Dict[str, Any]]:
        """Get the currently selected container."""
        table = self.query_one("#containers-table", DataTable)
        if table.cursor_row < len(self.filtered_containers):
            return self.filtered_containers[table.cursor_row]
        return None

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "search-input":
            self.filter_containers()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle DataTable row selection events (mouse click on row)."""
        # Just handle row selection, don't automatically show logs
        # Logs will only be shown when Enter key is pressed (action_logs_selected)
        pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        button_id = event.button.id
        container = self.get_selected_container()

        if button_id == "refresh-btn":
            self.refresh_containers()
        elif not container:
            self.notify("Please select a container first", severity="warning")
            return
        elif button_id == "restart-btn":
            self.restart_container(container)
        elif button_id == "logs-btn":
            self.show_logs(container)

    def restart_container(self, container_info: Dict[str, Any]) -> None:
        """Restart a container."""
        try:
            container = container_info["container_obj"]
            container.restart()
            self.notify(
                f"Restarted container: [blue]{container_info['name']}[/]",
                severity="information",
            )
            self.refresh_containers()
        except DockerException as e:
            self.notify(f"Failed to restart container: {e}", severity="error")

    def show_logs(self, container_info: Dict[str, Any]) -> None:
        """Show container logs."""
        try:
            container = container_info["container_obj"]
            self.app.push_screen(
                LogViewerScreen(container_info["name"], container.short_id)
            )
        except DockerException as e:
            self.notify(f"Failed to get logs: {e}", severity="error")

    def action_back(self) -> None:
        """Go back to main screen."""
        self.stop_auto_refresh()
        self.app.pop_screen()

    def action_refresh(self) -> None:
        """Refresh containers."""
        self.refresh_containers()

    def action_focus_toggle(self) -> None:
        """Toggle focus between search and table."""
        search_input = self.query_one("#search-input", Input)
        table = self.query_one("#containers-table", DataTable)
        if search_input.has_focus:
            table.focus()
        else:
            search_input.focus()

    def action_toggle_exited(self) -> None:
        """Toggle showing exited containers."""
        self.show_exited = not self.show_exited
        self.apply_filters()

    def action_toggle_auto_refresh(self) -> None:
        """Toggle auto-refresh functionality."""
        self.auto_refresh_enabled = not self.auto_refresh_enabled
        if self.auto_refresh_enabled:
            self.start_auto_refresh()
            self.notify(
                "Auto-refresh enabled (30s full, 1s uptime)", severity="information"
            )
        else:
            self.stop_auto_refresh()
            self.notify("Auto-refresh disabled", severity="information")

    def action_restart_selected(self) -> None:
        """Restart the selected container via keyboard."""
        container = self.get_selected_container()
        if container:
            self.restart_container(container)
        else:
            self.notify("Please select a container first", severity="warning")

    def action_logs_selected(self) -> None:
        """Show logs for the selected container via keyboard."""
        container = self.get_selected_container()
        if container:
            self.show_logs(container)
        else:
            self.notify("Please select a container first", severity="warning")

    def start_auto_refresh(self) -> None:
        """Start the auto-refresh timers."""
        if self.auto_refresh_enabled:
            # Full refresh every 30 seconds
            self.auto_refresh_timer = self.set_timer(30.0, self.auto_refresh_containers)
            # Uptime-only refresh every 1 seconds
            self.uptime_refresh_timer = self.set_timer(1.0, self.update_uptime_only)

    def stop_auto_refresh(self) -> None:
        """Stop the auto-refresh timers."""
        if self.auto_refresh_timer:
            self.auto_refresh_timer.stop()
            self.auto_refresh_timer = None
        if self.uptime_refresh_timer:
            self.uptime_refresh_timer.stop()
            self.uptime_refresh_timer = None

    def auto_refresh_containers(self) -> None:
        """Auto-refresh containers periodically."""
        self.refresh_containers()
        # Restart the timer for continuous refresh
        if self.auto_refresh_enabled:
            self.auto_refresh_timer = self.set_timer(30.0, self.auto_refresh_containers)

    def update_uptime_only(self) -> None:
        """Update uptime only without refreshing the entire container list."""
        COL_INDEX_UPTIME = self.column_names.index("Uptime")
        if (
            not self.auto_refresh_enabled
            or not self.docker_client
            or not self.filtered_containers
        ):
            return

        try:
            # Update uptime for running containers in the current filtered list
            table = self.query_one("#containers-table", DataTable)
            current_time = datetime.datetime.now(datetime.timezone.utc)

            for row_index, container_info in enumerate(self.filtered_containers):
                if container_info["status"] == "running":
                    container = container_info["container_obj"]
                    # Refresh container state
                    container.reload()

                    started_at = container.attrs.get("State", {}).get("StartedAt")
                    if started_at:
                        started_dt = datetime.datetime.fromisoformat(
                            started_at.replace("Z", "+00:00")
                        )
                        uptime_delta = current_time - started_dt

                        # Format uptime
                        days = uptime_delta.days
                        hours, remainder = divmod(uptime_delta.seconds, 3600)
                        minutes, seconds = divmod(remainder, 60)

                        if days > 0:
                            uptime_str = f"{days}d {hours}h {minutes}m"
                        else:
                            uptime_str = f"{hours}h {minutes}m {seconds}s"

                        # Update the container info and table cell
                        container_info["uptime"] = uptime_str
                        table.update_cell_at(
                            Coordinate(row_index, COL_INDEX_UPTIME), uptime_str
                        )

            # Restart the timer for continuous refresh
            if self.auto_refresh_enabled:
                self.uptime_refresh_timer = self.set_timer(1.0, self.update_uptime_only)

        except Exception:
            # If there's any error, just skip this update cycle
            if self.auto_refresh_enabled:
                self.uptime_refresh_timer = self.set_timer(1.0, self.update_uptime_only)

    async def on_key(self, event: Key) -> None:
        """Handle key events globally for the screen."""
        search_input = self.query_one("#search-input", Input)
        table = self.query_one("#containers-table", DataTable)

        # If table is focused and we get enter, show logs
        if table.has_focus and event.key == "enter":
            self.action_logs_selected()
            event.prevent_default()
            return

        # If input is focused and we get arrow keys or enter, forward to table
        if search_input.has_focus:
            if event.key == "up":
                # Move table cursor up using action
                await table.run_action("cursor_up")
                event.prevent_default()
                return
            elif event.key == "down":
                # Move table cursor down using action
                await table.run_action("cursor_down")
                event.prevent_default()
                return
            elif event.key == "enter":
                # Trigger logs for selected container
                self.action_logs_selected()
                event.prevent_default()
                return
            elif event.key == "ctrl+r":
                # Restart selected container
                self.action_restart_selected()
                event.prevent_default()
                return

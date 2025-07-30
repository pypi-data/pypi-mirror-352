from . import __version__
from textual.app import App, ComposeResult, SystemCommand
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Header, Footer, Label
from textual.binding import Binding
from textual.screen import Screen
from .containers import ContainerScreen
from typing import Iterable


class DockieApp(App):
    """A Textual app for Docker Container Management."""

    CSS_PATH = "app.tcss"
    TITLE = "Dockie - Docker Container Manager"
    BINDINGS = [
        Binding("escape", "quit", "Exit"),
        Binding("ctrl+q", "quit", "Quit"),
    ]

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        """Get system commands for the command palette.

        Only includes theme change and quit commands, removing all other defaults.
        """
        # Only yield the specific commands we want to keep
        yield SystemCommand(
            "Change theme", "Change the current theme", self.action_change_theme
        )
        yield SystemCommand(
            "Quit the application",
            "Quit the application as soon as possible",
            self.action_quit,
        )

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)
        yield Container(
            Vertical(
                Label(f"🐳 Dockie v2 {__version__}", classes="title"),
                Label(
                    "A streamlined Docker container management interface",
                    classes="subtitle",
                ),
                Horizontal(
                    Button("📦 Manage Containers", id="containers", variant="primary"),
                    Button("🚀 More coming ...", id="more", variant="default"),
                    classes="button-group",
                ),
                classes="main-container",
            ),
            id="main",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the app and go directly to containers."""
        # Automatically show containers on startup for a streamlined experience
        self.call_after_refresh(self.show_containers)

    def show_containers(self) -> None:
        """Show the container screen."""
        self.push_screen(ContainerScreen())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        button_id = event.button.id
        if button_id == "containers":
            self.show_containers()
        # elif button_id == "...":

    def action_containers(self) -> None:
        """Show containers via keybinding."""
        self.show_containers()


def main():
    """Run the Dockie application."""
    app = DockieApp()
    app.run()


if __name__ == "__main__":
    main()

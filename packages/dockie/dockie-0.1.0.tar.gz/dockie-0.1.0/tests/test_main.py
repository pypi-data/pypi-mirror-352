"""Tests for the main application."""

from main import DockieApp


def test_app_creation():
    """Test that the app can be created."""
    app = DockieApp()
    assert app.title == "Dockie - Docker TUI Manager"


def test_app_bindings():
    """Test that the app has the expected key bindings."""
    app = DockieApp()
    binding_keys = [binding.key for binding in app.BINDINGS]
    assert "q" in binding_keys
    assert "ctrl+c" in binding_keys 
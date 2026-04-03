"""Helper functions for VK Teams integration."""

from .const import SIGNAL_UPDATE_EVENT


def signal(bot_id: str) -> str:
    """Define signal name."""
    return f"{SIGNAL_UPDATE_EVENT}_{bot_id}"
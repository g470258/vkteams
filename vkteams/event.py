"""Event platform for VK Teams integration."""

import logging
from typing import Any

from homeassistant.components.event import EventEntity, EventEntityDescription
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN, EVENT_CALLBACK, EVENT_COMMAND, EVENT_TEXT, EVENT_MESSAGE_SENT,
    ATTR_ARGS, ATTR_CALLBACK_DATA, ATTR_CHAT_ID, ATTR_COMMAND, ATTR_DATA,
    ATTR_DATE, ATTR_FROM_FIRST, ATTR_FROM_LAST, ATTR_ID, ATTR_MESSAGE,
    ATTR_MESSAGE_ID, ATTR_TEXT, ATTR_USER_ID,
)
from .entity import VKTeamsEntity
from .helpers import signal

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the event platform for the main bot."""
    _LOGGER.info("Setting up VK Teams event entity")
    
    entry_id = config_entry.entry_id
    bot_name = config_entry.title
    
    event_entity = VKTeamsEventEntity(entry_id, bot_name, hass)
    async_add_entities([event_entity])


class VKTeamsEventEntity(VKTeamsEntity, EventEntity):
    """Event entity for VK Teams bot updates (main bot device)."""

    _attr_event_types = [
        EVENT_CALLBACK,
        EVENT_COMMAND,
        EVENT_TEXT,
        EVENT_MESSAGE_SENT,
    ]

    def __init__(self, device_id: str, device_name: str, hass: HomeAssistant) -> None:
        """Initialize the entity."""
        self.hass = hass
        self._device_id = device_id
        
        super().__init__(
            device_id=device_id,
            device_name=device_name,
            entity_description=EventEntityDescription(
                key="update_event", 
                translation_key="update_event"
            ),
        )
        self._attr_name = "Bot updates"

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                signal(self._device_id),
                self._async_handle_event,
            )
        )

    @callback
    def _async_handle_event(self, event_type: str, event_data: dict[str, Any]) -> None:
        """Handle the event."""
        self._trigger_event(event_type, event_data)
        self.async_write_ha_state()
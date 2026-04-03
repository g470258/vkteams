"""Notify platform for VK Teams integration."""

import logging
from homeassistant.components.notify import NotifyEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN, CONF_CHAT_ID, CONF_PARSE_MODE, DEFAULT_PARSE_MODE, SUBENTRY_TYPE_ALLOWED_CHAT_IDS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up notify entities for each allowed chat subentry."""
    _LOGGER.info("Setting up VK Teams notify entities")
    
    bot = hass.data[DOMAIN][config_entry.entry_id]["bot"]
    parse_mode = config_entry.data.get(CONF_PARSE_MODE, DEFAULT_PARSE_MODE)
    
    entities = []
    
    for subentry_id, subentry in config_entry.subentries.items():
        if subentry.subentry_type == SUBENTRY_TYPE_ALLOWED_CHAT_IDS:
            chat_id = subentry.data.get(CONF_CHAT_ID)
            if chat_id:
                entity = VKTeamsNotifyEntity(
                    bot=bot,
                    chat_id=chat_id,
                    parse_mode=parse_mode,
                    subentry=subentry,
                )
                async_add_entities([entity], config_subentry_id=subentry_id)


class VKTeamsNotifyEntity(NotifyEntity, RestoreEntity):
    """Notify entity for VK Teams chat."""

    def __init__(self, bot, chat_id: str, parse_mode: str, subentry):
        """Initialize the entity."""
        self.bot = bot
        self.chat_id = chat_id
        self.parse_mode = parse_mode
        
        safe_chat_id = chat_id.replace("@", "_at_").replace(".", "_").replace("-", "_")
        
        self._attr_unique_id = f"vkteams_notify_{subentry.subentry_id}"
        self._attr_name = subentry.title
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, subentry.subentry_id)},
            "name": subentry.title,
            "manufacturer": "VK Teams",
            "model": "Bot API",
            "entry_type": "service",
        }
        
        self.entity_id = f"notify.vkteams_{safe_chat_id}"

    async def async_send_message(self, message: str, title: str | None = None) -> None:
        """Send a message to the chat."""
        if title:
            message = f"*{title}*\n{message}"
        
        await self.bot.send_text(
            chat_id=self.chat_id,
            text=message,
            parse_mode=self.parse_mode if self.parse_mode != "plain_text" else None,
        )
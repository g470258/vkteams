"""Base entity for VK Teams integration."""

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity import Entity, EntityDescription

from .const import DOMAIN


class VKTeamsEntity(Entity):
    """Base entity for VK Teams."""

    _attr_has_entity_name = True

    def __init__(
        self,
        device_id: str,
        device_name: str,
        entity_description: EntityDescription,
    ) -> None:
        """Initialize the entity."""
        self.entity_description = entity_description
        self._attr_unique_id = f"{device_id}_{entity_description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=device_name,  # Имя устройства
            manufacturer="VK Teams",
            model="Bot API",
            entry_type=DeviceEntryType.SERVICE,
        )
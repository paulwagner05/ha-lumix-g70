import logging
from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN, DELAY_IMAGE_PROCESSING_SECONDS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Panasonic Lumix G70 number based on a config entry."""
    client = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([LumixDelayNumber(client, entry)])


class LumixDelayNumber(NumberEntity, RestoreEntity):
    """Representation of an Image Processing Delay Number for the Lumix G70."""

    _attr_has_entity_name = True
    _attr_name = "Image Processing Delay"
    _attr_icon = "mdi:timer-outline"
    _attr_native_min_value = 0.0
    _attr_native_max_value = 10.0
    _attr_native_step = 0.1
    _attr_mode = NumberMode.BOX

    def __init__(self, client, entry: ConfigEntry) -> None:
        """Initialize the number entity."""
        self._client = client
        self._entry = entry
        
        # Unique ID based on the config entry ID
        self._attr_unique_id = f"{entry.entry_id}_image_processing_delay"
        self._attr_native_value = float(DELAY_IMAGE_PROCESSING_SECONDS)

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this entity."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=f"Lumix G70 ({self._client.ip_address})",
            manufacturer="Panasonic",
            model="Lumix G70",
            configuration_url=f"http://{self._client.ip_address}/",
        )

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        state = await self.async_get_last_state()
        
        if state is not None and state.state is not None:
            try:
                self._attr_native_value = float(state.state)
            except ValueError:
                self._attr_native_value = float(DELAY_IMAGE_PROCESSING_SECONDS)
                
        self._client.delay_image_processing_seconds = self._attr_native_value

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        self._attr_native_value = value
        self._client.delay_image_processing_seconds = value
        self.async_write_ha_state()

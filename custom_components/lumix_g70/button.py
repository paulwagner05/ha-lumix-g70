import asyncio
import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    COMMAND_MODE_CAMERA,
    COMMAND_VALUE_RECORD_MODE,
    COMMAND_VALUE_CAPTURE,
    COMMAND_VALUE_PLAY_MODE,
    DELAY_LENS_EXTENSION_SECONDS,
    DELAY_IMAGE_PROCESSING_SECONDS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Panasonic Lumix G70 button based on a config entry."""
    client = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([LumixTakePhotoButton(client, entry)])


class LumixTakePhotoButton(ButtonEntity):
    """Representation of a Take Photo button for the Lumix G70."""

    _attr_has_entity_name = True
    _attr_name = "Take Photo"
    _attr_icon = "mdi:camera-iris"

    def __init__(self, client, entry: ConfigEntry) -> None:
        """Initialize the button."""
        self._client = client
        self._entry = entry
        
        # Unique ID based on the config entry ID
        self._attr_unique_id = f"{entry.entry_id}_take_photo"

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

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.debug("Taking photo on Lumix G70 at %s", self._client.ip_address)
        
        record_mode_activated = await self._client.async_send_command(
            mode=COMMAND_MODE_CAMERA, value=COMMAND_VALUE_RECORD_MODE
        )

        if not record_mode_activated:
            _LOGGER.error("Failed to wake up camera. Aborting photo sequence.")
            return

        await asyncio.sleep(DELAY_LENS_EXTENSION_SECONDS)

        try:
            await self._client.async_send_command(
                mode=COMMAND_MODE_CAMERA, value=COMMAND_VALUE_CAPTURE
            )
            await asyncio.sleep(DELAY_IMAGE_PROCESSING_SECONDS)

        finally:
            await self._client.async_send_command(
                mode=COMMAND_MODE_CAMERA, value=COMMAND_VALUE_PLAY_MODE
            )

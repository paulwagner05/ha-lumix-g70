import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN, DEFAULT_RETURN_TO_PLAY_MODE

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Panasonic Lumix G70 switch based on a config entry."""
    client = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([LumixReturnToPlayModeSwitch(client, entry)])


class LumixReturnToPlayModeSwitch(SwitchEntity, RestoreEntity):
    """Representation of a Return to Play Mode Switch for the Lumix G70."""

    _attr_has_entity_name = True
    _attr_name = "Return to Play Mode"
    _attr_icon = "mdi:camera-control"

    def __init__(self, client, entry: ConfigEntry) -> None:
        """Initialize the switch."""
        self._client = client
        self._entry = entry
        
        # Unique ID based on the config entry ID
        self._attr_unique_id = f"{entry.entry_id}_return_to_play_mode"
        self._attr_is_on = DEFAULT_RETURN_TO_PLAY_MODE

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
            self._attr_is_on = state.state == "on"
            
        self._client.return_to_play_mode = self._attr_is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        self._attr_is_on = True
        self._client.return_to_play_mode = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        self._attr_is_on = False
        self._client.return_to_play_mode = False
        self.async_write_ha_state()

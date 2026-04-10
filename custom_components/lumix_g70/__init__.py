import logging
import asyncio
import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_IP_ADDRESS,
    API_ENDPOINT,
    REQUEST_TIMEOUT_SECONDS,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["button"]


class LumixCameraClient:
    """Client for controlling the Panasonic Lumix G70."""

    def __init__(self, ip_address: str, session: aiohttp.ClientSession) -> None:
        self._base_url = f"http://{ip_address}/{API_ENDPOINT}"
        self._session = session
        self.ip_address = ip_address

    async def async_send_command(self, mode: str, value: str) -> bool:
        """Send a command to the camera."""
        request_url = f"{self._base_url}?mode={mode}&value={value}"

        try:
            async with self._session.get(
                request_url, timeout=REQUEST_TIMEOUT_SECONDS
            ) as response:
                response.raise_for_status()
                return True

        except asyncio.TimeoutError:
            _LOGGER.error("Camera request timed out for command: '%s'", value)
            return False

        except aiohttp.ClientResponseError as error:
            _LOGGER.error(
                "Camera rejected command '%s' with HTTP status: %s", value, error.status
            )
            return False

        except aiohttp.ClientError as error:
            _LOGGER.error(
                "Network connection error while sending command '%s': %s", value, error
            )
            return False


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Panasonic Lumix G70 component."""
    # YAML configuration is no longer supported, but we keep setup to initialize the domain
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Panasonic Lumix G70 from a config entry."""
    ip_address = entry.data[CONF_IP_ADDRESS]
    session = async_get_clientsession(hass)
    client = LumixCameraClient(ip_address, session)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = client

    # Forward the setup to the button platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

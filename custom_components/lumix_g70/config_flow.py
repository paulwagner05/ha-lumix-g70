import logging
import aiohttp
import asyncio
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_IP_ADDRESS,
    API_ENDPOINT,
    REQUEST_TIMEOUT_SECONDS,
    CONF_RETURN_TO_PLAY_MODE,
    DEFAULT_RETURN_TO_PLAY_MODE,
)

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_IP_ADDRESS): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict) -> dict:
    """Validate the user input allows us to connect."""
    ip_address = data[CONF_IP_ADDRESS]
    session = async_get_clientsession(hass)
    
    # Try to reach the camera to verify IP
    url = f"http://{ip_address}/{API_ENDPOINT}?mode=camcmd&value=playmode"
    try:
        async with session.get(url, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            if response.status != 200:
                raise CannotConnect
    except (asyncio.TimeoutError, aiohttp.ClientError):
        raise CannotConnect

    return {"title": f"Lumix G70 ({ip_address})"}


class LumixG70ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Panasonic Lumix G70."""

    VERSION = 1



    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            self._async_abort_entries_match({CONF_IP_ADDRESS: user_input[CONF_IP_ADDRESS]})

            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data=user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )



class CannotConnect(Exception):
    """Error to indicate we cannot connect."""

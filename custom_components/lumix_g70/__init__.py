import logging
import asyncio
import aiohttp
import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as config_validation

_LOGGER = logging.getLogger(__name__)

DOMAIN = "lumix_g70"
CONF_IP_ADDRESS = "ip_address"
API_ENDPOINT = "cam.cgi"

COMMAND_MODE_CAMERA = "camcmd"
COMMAND_VALUE_RECORD_MODE = "recmode"
COMMAND_VALUE_CAPTURE = "capture"
COMMAND_VALUE_PLAY_MODE = "playmode"

DELAY_LENS_EXTENSION_SECONDS = 2.0
DELAY_IMAGE_PROCESSING_SECONDS = 1.5
REQUEST_TIMEOUT_SECONDS = 5.0

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_IP_ADDRESS): config_validation.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


class LumixCameraClient:

    def __init__(self, ip_address: str, session: aiohttp.ClientSession) -> None:
        self._base_url = f"http://{ip_address}/{API_ENDPOINT}"
        self._session = session

    async def async_send_command(self, mode: str, value: str) -> bool:
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


async def async_setup(
    home_assistant_instance: HomeAssistant, configuration: dict
) -> bool:
    domain_configuration = configuration.get(DOMAIN)

    if domain_configuration is None:
        return True

    ip_address = domain_configuration.get(CONF_IP_ADDRESS)
    client_session = async_get_clientsession(home_assistant_instance)
    camera_client = LumixCameraClient(ip_address, client_session)

    async def async_handle_take_photo_service(service_call: ServiceCall) -> None:
        record_mode_activated = await camera_client.async_send_command(
            mode=COMMAND_MODE_CAMERA, value=COMMAND_VALUE_RECORD_MODE
        )

        if not record_mode_activated:
            _LOGGER.error("Failed to wake up camera. Aborting photo sequence.")
            return

        await asyncio.sleep(DELAY_LENS_EXTENSION_SECONDS)

        try:
            await camera_client.async_send_command(
                mode=COMMAND_MODE_CAMERA, value=COMMAND_VALUE_CAPTURE
            )
            await asyncio.sleep(DELAY_IMAGE_PROCESSING_SECONDS)

        finally:
            await camera_client.async_send_command(
                mode=COMMAND_MODE_CAMERA, value=COMMAND_VALUE_PLAY_MODE
            )

    home_assistant_instance.services.async_register(
        domain=DOMAIN,
        service="take_photo",
        service_func=async_handle_take_photo_service,
    )

    return True

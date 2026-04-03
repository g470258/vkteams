"""Config flow for VK Teams integration."""

import logging
import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    DOMAIN, CONF_TOKEN, CONF_API_URL, CONF_CHAT_ID,
    CONF_PARSE_MODE, CONF_POLL_INTERVAL, DEFAULT_API_URL, DEFAULT_PARSE_MODE,
    DEFAULT_POLL_INTERVAL, PARSE_MODES, SUBENTRY_TYPE_ALLOWED_CHAT_IDS
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_TOKEN): TextSelector(
        TextSelectorConfig(type=TextSelectorType.PASSWORD)
    ),
    vol.Optional(CONF_API_URL, default=DEFAULT_API_URL): TextSelector(
        TextSelectorConfig(type=TextSelectorType.URL)
    ),
    vol.Optional(CONF_PARSE_MODE, default=DEFAULT_PARSE_MODE): vol.In(PARSE_MODES),
    vol.Optional(CONF_POLL_INTERVAL, default=DEFAULT_POLL_INTERVAL): int,
})

SUBENTRY_SCHEMA = vol.Schema({
    vol.Required(CONF_CHAT_ID): str,
})


async def validate_token(hass: HomeAssistant, token: str, api_url: str) -> tuple[bool, dict | None]:
    """Validate the token and return bot info."""
    async with aiohttp.ClientSession() as session:
        url = f"{api_url}/bot/v1/self/get"
        params = {"token": token}
        try:
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    return False, None
                result = await resp.json()
                if result.get("ok"):
                    bot_info = result.get("bot", {})
                    return True, {
                        "firstName": result.get("firstName", "VK Teams Bot"),
                        "nick": result.get("nick", ""),
                        "userId": result.get("userId", ""),
                    }
                return False, None
        except Exception:
            return False, None


async def validate_chat_id(token: str, api_url: str, chat_id: str) -> tuple[bool, dict | None]:
    """Validate chat ID and return info (supports users and groups)."""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{api_url}/bot/v1/chats/getInfo"
            params = {"token": token, "chatId": chat_id}
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    return False, None
                result = await resp.json()
                if result.get("ok"):
                    chat_type = result.get("type")
                    return True, {
                        "type": chat_type,
                        "title": result.get("title", ""),
                        "firstName": result.get("firstName", ""),
                        "lastName": result.get("lastName", ""),
                    }
                return False, None
    except Exception:
        return False, None


class VKTeamsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for VK Teams."""

    VERSION = 1

    @classmethod
    @callback
    def async_get_supported_subentry_types(cls, config_entry):
        """Return subentries supported by this integration."""
        return {SUBENTRY_TYPE_ALLOWED_CHAT_IDS: AllowedChatIdsSubEntryFlowHandler}

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            valid, bot_info = await validate_token(
                self.hass,
                user_input[CONF_TOKEN],
                user_input[CONF_API_URL]
            )
            
            if valid:
                await self.async_set_unique_id(user_input[CONF_TOKEN])
                self._abort_if_unique_id_configured()
                
                bot_name = bot_info.get("firstName") or bot_info.get("nick") or "VK Teams Bot"
                
                return self.async_create_entry(
                    title=bot_name,
                    data=user_input,
                )
            else:
                errors["base"] = "invalid_auth"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class AllowedChatIdsSubEntryFlowHandler(config_entries.ConfigSubentryFlow):
    """Handle subentry flow for adding allowed chat IDs."""

    async def async_step_user(self, user_input: dict | None = None) -> config_entries.SubentryFlowResult:
        """Add allowed chat ID."""
        errors = {}

        if user_input is not None:
            chat_id = user_input[CONF_CHAT_ID]
            
            if not chat_id:
                errors["base"] = "invalid_chat_id"
            else:
                entry = self._get_entry()
                token = entry.data[CONF_TOKEN]
                api_url = entry.data.get(CONF_API_URL, DEFAULT_API_URL)
                
                valid, chat_info = await validate_chat_id(token, api_url, chat_id)
                
                if not valid:
                    errors["base"] = "chat_not_found"
                else:
                    chat_type = chat_info.get("type")
                    
                    if chat_type == "private":
                        first_name = chat_info.get("firstName", "")
                        last_name = chat_info.get("lastName", "")
                        if last_name or first_name:
                            display_name = f"{last_name} {first_name} ({chat_id})".strip()
                        else:
                            display_name = chat_id
                    elif chat_type == "group":
                        title = chat_info.get("title", "")
                        if title:
                            display_name = f"{title} ({chat_id})"
                        else:
                            display_name = chat_id
                    else:
                        display_name = chat_id
                    
                    return self.async_create_entry(
                        title=display_name,
                        data={CONF_CHAT_ID: chat_id},
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=SUBENTRY_SCHEMA,
            errors=errors,
            description_placeholders={
                "help_text": "Введите ID чата или пользователя\n\n- Для пользователя: user@example.com\n- Для группы: 123456789@chat.agent"
            },
        )
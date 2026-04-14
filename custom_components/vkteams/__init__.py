"""VK Teams integration for Home Assistant."""

import logging
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.dispatcher import async_dispatcher_send
import voluptuous as vol

from .const import (
    DOMAIN, CONF_TOKEN, CONF_API_URL, CONF_CHAT_ID,
    CONF_PARSE_MODE, CONF_POLL_INTERVAL, DEFAULT_PARSE_MODE, DEFAULT_POLL_INTERVAL,
    EVENT_CALLBACK, EVENT_COMMAND, EVENT_TEXT, EVENT_MESSAGE_SENT,
    SUBENTRY_TYPE_ALLOWED_CHAT_IDS
)
from .bot import VKTeamsBot
from .helpers import signal

_LOGGER = logging.getLogger(__name__)

# Service schemas
SERVICE_SEND_MESSAGE_SCHEMA = vol.Schema({
    vol.Required("message"): cv.string,
    vol.Optional("entity_id"): vol.Any(cv.entity_id, [cv.entity_id]),
    vol.Optional("chat_id"): vol.Any(cv.string, [cv.string]),
    vol.Optional("title"): cv.string,
    vol.Optional("parse_mode"): vol.In(["HTML", "MarkdownV2"]),
    vol.Optional("buttons"): list,
    vol.Optional("buttons_layout"): vol.In(["row", "column"]),
    vol.Optional("disable_notification"): cv.boolean,
})

SERVICE_SEND_PHOTO_SCHEMA = vol.Schema(
    {
        vol.Required("url", default=None): vol.Any(cv.string, None),
        vol.Optional("file"): cv.string,
        vol.Optional("caption"): cv.string,
        vol.Optional("entity_id"): vol.Any(cv.entity_id, [cv.entity_id]),
        vol.Optional("chat_id"): vol.Any(cv.string, [cv.string]),
        vol.Optional("buttons"): list,
        vol.Optional("buttons_layout"): vol.In(["row", "column"]),
        vol.Optional("disable_notification"): cv.boolean,
    },
    extra=vol.ALLOW_EXTRA,
)

SERVICE_SEND_VIDEO_SCHEMA = vol.Schema(
    {
        vol.Required("url", default=None): vol.Any(cv.string, None),
        vol.Optional("file"): cv.string,
        vol.Optional("caption"): cv.string,
        vol.Optional("entity_id"): vol.Any(cv.entity_id, [cv.entity_id]),
        vol.Optional("chat_id"): vol.Any(cv.string, [cv.string]),
        vol.Optional("buttons"): list,
        vol.Optional("buttons_layout"): vol.In(["row", "column"]),
        vol.Optional("disable_notification"): cv.boolean,
    },
    extra=vol.ALLOW_EXTRA,
)

SERVICE_EDIT_MESSAGE_SCHEMA = vol.Schema({
    vol.Required("message_id"): int,
    vol.Required("message"): cv.string,
    vol.Optional("entity_id"): cv.entity_id,
    vol.Optional("chat_id"): cv.string,
    vol.Optional("parse_mode"): vol.In(["HTML", "MarkdownV2"]),
    vol.Optional("buttons"): list,
    vol.Optional("buttons_layout"): vol.In(["row", "column"]),
})

SERVICE_DELETE_MESSAGES_SCHEMA = vol.Schema({
    vol.Required("message_ids"): vol.All(cv.ensure_list, [int]),
    vol.Optional("entity_id"): cv.entity_id,
    vol.Optional("chat_id"): cv.string,
})

SERVICE_ANSWER_CALLBACK_SCHEMA = vol.Schema({
    vol.Required("query_id"): cv.string,
    vol.Optional("text"): cv.string,
    vol.Optional("show_alert"): cv.boolean,
    vol.Optional("url"): cv.string,
})


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the VK Teams integration."""
    return True


def _get_chat_id_from_entity_id(hass: HomeAssistant, entry: ConfigEntry, entity_id: str) -> str | None:
    """Extract chat_id from notify entity_id."""
    if not entity_id or not entity_id.startswith("notify.vkteams_"):
        return None
    
    suffix = entity_id[15:]  # убираем "notify.vkteams_"
    
    for subentry in entry.subentries.values():
        if subentry.subentry_type == SUBENTRY_TYPE_ALLOWED_CHAT_IDS:
            chat_id = subentry.data.get(CONF_CHAT_ID)
            safe_chat_id = chat_id.replace("@", "_at_").replace(".", "_").replace("-", "_")
            if suffix == safe_chat_id:
                return chat_id
    
    return None


def _get_chat_ids_from_entity_ids(hass: HomeAssistant, entry: ConfigEntry, entity_ids) -> list[str]:
    """Extract chat_ids from list of entity_ids."""
    if not entity_ids:
        return []
    
    if not isinstance(entity_ids, list):
        entity_ids = [entity_ids]
    
    chat_ids = []
    for entity_id in entity_ids:
        chat_id = _get_chat_id_from_entity_id(hass, entry, entity_id)
        if chat_id:
            chat_ids.append(chat_id)
    
    return chat_ids


def _get_chat_ids_from_params(hass: HomeAssistant, entry: ConfigEntry, call: ServiceCall, allowed_chats: list) -> list[str]:
    """Get chat_ids from entity_id, chat_id, or use default."""
    
    # 1. Проверяем entity_id
    entity_ids = call.data.get("entity_id")
    if entity_ids:
        chat_ids = _get_chat_ids_from_entity_ids(hass, entry, entity_ids)
        if chat_ids:
            return chat_ids
    
    # 2. Проверяем chat_id
    chat_ids = call.data.get("chat_id")
    if chat_ids:
        if not isinstance(chat_ids, list):
            chat_ids = [chat_ids]
        return chat_ids
    
    # 3. Используем первый разрешённый чат
    if allowed_chats:
        return [allowed_chats[0]]
    
    return []


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up VK Teams from a config entry."""
    _LOGGER.info("Setting up VK Teams integration")
    
    hass.data.setdefault(DOMAIN, {})
    
    bot = VKTeamsBot(
        token=entry.data[CONF_TOKEN],
        api_url=entry.data[CONF_API_URL]
    )
    
    # Получаем список разрешённых чатов из subentries
    allowed_chats = []
    for subentry in entry.subentries.values():
        if subentry.subentry_type == SUBENTRY_TYPE_ALLOWED_CHAT_IDS:
            chat_id = subentry.data.get(CONF_CHAT_ID)
            if chat_id:
                allowed_chats.append(chat_id)
    
    _LOGGER.info(f"Allowed chats: {allowed_chats}")
    
    hass.data[DOMAIN][entry.entry_id] = {
        "bot": bot,
        "config": entry.data,
        "allowed_chats": allowed_chats,
    }
    
    parse_mode = entry.data.get(CONF_PARSE_MODE, DEFAULT_PARSE_MODE)
    
    # Build keyboard helper
    def build_keyboard(buttons: list, layout: str = "row") -> list:
        """Build inline keyboard markup.
        
        Args:
            buttons: Either:
                - List of buttons for row layout: [{"text": "Btn1"}, {"text": "Btn2"}]
                - List of rows for grid layout: [[{"text": "Btn1"}, {"text": "Btn2"}], [{"text": "Btn3"}]]
            layout: 
                - "row" (default): all buttons in one horizontal row
                - Any other value: ignored, buttons structure defines the layout
        """
        if not buttons:
            return None
        
        # Если первый элемент - список (массив массивов) -> это сетка
        if buttons and isinstance(buttons[0], list):
            rows = []
            for row in buttons:
                buttons_row = []
                for btn in row:
                    buttons_row.append({
                        "text": btn["text"],
                        "callbackData": btn.get("callbackData", btn["text"]),
                        "style": btn.get("style", "default")
                    })
                rows.append(buttons_row)
            return rows
        
        # Иначе - все кнопки в одной строке (горизонтально)
        row = []
        for btn in buttons:
            row.append({
                "text": btn["text"],
                "callbackData": btn.get("callbackData", btn["text"]),
                "style": btn.get("style", "default")
            })
        return [row]
    
    # Event handler
    async def handle_event(event: dict):
        """Handle incoming events from long polling."""
        event_type = event.get("type")
        
        if event_type == "callbackQuery":
            payload = event.get("payload", {})
            callback_data = payload.get("callbackData")
            query_id = payload.get("queryId")
            message = payload.get("message", {})
            chat_id = message.get("chat", {}).get("chatId")
            user = payload.get("from", {})
            
            # Получаем актуальный список разрешённых чатов из subentries
            allowed_chats_list = []
            for subentry in entry.subentries.values():
                if subentry.subentry_type == SUBENTRY_TYPE_ALLOWED_CHAT_IDS:
                    allowed_chats_list.append(subentry.data.get(CONF_CHAT_ID))
            
            if chat_id not in allowed_chats_list:
                _LOGGER.info(f"Ignoring callback from unauthorized chat: {chat_id}")
                await bot.answer_callback(query_id=query_id, text="❌ Чат не разрешён", show_alert=True)
                return
            
            _LOGGER.info(f"Callback received: {callback_data}")
            
            event_data = {
                "id": query_id,
                "data": callback_data,
                "chat_id": chat_id,
                "user_id": user.get("userId"),
                "user_name": f"{user.get('firstName', '')} {user.get('lastName', '')}".strip(),
                "message": message,
            }
            
            hass.bus.async_fire(EVENT_CALLBACK, event_data)
            async_dispatcher_send(hass, signal(entry.entry_id), EVENT_CALLBACK, event_data)
            
            await bot.answer_callback(query_id=query_id, text="✅", show_alert=False)
            
        elif event_type == "newMessage":
            payload = event.get("payload", {})
            text = payload.get("text", "")
            chat_id = payload.get("chat", {}).get("chatId")
            user = payload.get("from", {})
            msg_id = payload.get("msgId")
            
            # Получаем актуальный список разрешённых чатов из subentries
            allowed_chats_list = []
            for subentry in entry.subentries.values():
                if subentry.subentry_type == SUBENTRY_TYPE_ALLOWED_CHAT_IDS:
                    allowed_chats_list.append(subentry.data.get(CONF_CHAT_ID))
            
            # Проверяем, разрешён ли чат
            if chat_id not in allowed_chats_list:
                _LOGGER.info(f"Ignoring message from unauthorized chat: {chat_id}")
                await bot.send_text(
                    chat_id=chat_id,
                    text="❌ Ваш chat_id не добавлен в список разрешённых.\n\n"
                         "Чтобы бот отвечал вам, добавьте этот chat_id через кнопку '+' в интеграции VK Teams Bot.\n\n"
                         f"Ваш chat_id: `{chat_id}`"
                )
                return
            
            if text.startswith("/"):
                parts = text.split()
                command = parts[0]
                args = " ".join(parts[1:]) if len(parts) > 1 else ""
                
                _LOGGER.info(f"Command received: {command}")
                
                event_data = {
                    "command": command,
                    "args": args,
                    "chat_id": chat_id,
                    "user_id": user.get("userId"),
                    "user_name": f"{user.get('firstName', '')} {user.get('lastName', '')}".strip(),
                    "text": text,
                }
                
                hass.bus.async_fire(EVENT_COMMAND, event_data)
                async_dispatcher_send(hass, signal(entry.entry_id), EVENT_COMMAND, event_data)
            else:
                _LOGGER.debug(f"Text received: {text[:50]}")
                
                event_data = {
                    "text": text,
                    "chat_id": chat_id,
                    "user_id": user.get("userId"),
                    "user_name": f"{user.get('firstName', '')} {user.get('lastName', '')}".strip(),
                    "msg_id": msg_id,
                }
                
                hass.bus.async_fire(EVENT_TEXT, event_data)
                async_dispatcher_send(hass, signal(entry.entry_id), EVENT_TEXT, event_data)
    
    # Start polling
    poll_interval = entry.data.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)
    await bot.start_polling(handle_event, poll_time=poll_interval)
    
    # Service handlers
    async def send_message(call: ServiceCall):
        """Send a message."""
        chat_ids = _get_chat_ids_from_params(hass, entry, call, allowed_chats)
        if not chat_ids:
            _LOGGER.error("No valid target found (entity_id, chat_id, or default chat)")
            return
        
        buttons = call.data.get("buttons")
        layout = call.data.get("buttons_layout", "row")
        inline_keyboard = build_keyboard(buttons, layout) if buttons else None
        msg_parse_mode = call.data.get("parse_mode", parse_mode)
        title = call.data.get("title")
        
        message_text = call.data["message"]
        if title:
            if msg_parse_mode == "HTML":
                message_text = f"<b>{title}</b>\n{message_text}"
            elif msg_parse_mode == "MarkdownV2":
                message_text = f"*{title}*\n{message_text}"
            else:
                message_text = f"{title}\n{message_text}"
        
        for chat_id in chat_ids:
            result = await bot.send_text(
                chat_id=chat_id,
                text=message_text,
                parse_mode=msg_parse_mode,
                inline_keyboard=inline_keyboard
            )
            
            if result.get("ok") and result.get("msgId"):
                event_data = {
                    "chat_id": chat_id,
                    "message_id": result["msgId"],
                    "text": call.data["message"][:100],
                }
                hass.bus.async_fire(EVENT_MESSAGE_SENT, event_data)
                async_dispatcher_send(hass, signal(entry.entry_id), EVENT_MESSAGE_SENT, event_data)
    
    async def send_photo(call: ServiceCall):
        """Send a photo."""
        chat_ids = _get_chat_ids_from_params(hass, entry, call, allowed_chats)
        if not chat_ids:
            _LOGGER.error("No valid target found (entity_id, chat_id, or default chat)")
            return
        
        buttons = call.data.get("buttons")
        layout = call.data.get("buttons_layout", "row")
        inline_keyboard = build_keyboard(buttons, layout) if buttons else None
        msg_parse_mode = call.data.get("parse_mode", parse_mode)
        caption = call.data.get("caption")
        
        url = call.data.get("url")
        file_path = call.data.get("file")
        
        for chat_id in chat_ids:
            result = await bot.send_photo(
                chat_id=chat_id,
                photo_url=url,
                photo_path=file_path,
                caption=caption,
                parse_mode=msg_parse_mode,
                inline_keyboard=inline_keyboard
            )
            
            if result.get("ok") and result.get("msgId"):
                event_data = {
                    "chat_id": chat_id,
                    "message_id": result["msgId"],
                }
                hass.bus.async_fire(EVENT_MESSAGE_SENT, event_data)
                async_dispatcher_send(hass, signal(entry.entry_id), EVENT_MESSAGE_SENT, event_data)
    
    async def send_video(call: ServiceCall):
        """Send a video."""
        chat_ids = _get_chat_ids_from_params(hass, entry, call, allowed_chats)
        if not chat_ids:
            _LOGGER.error("No valid target found (entity_id, chat_id, or default chat)")
            return
        
        buttons = call.data.get("buttons")
        layout = call.data.get("buttons_layout", "row")
        inline_keyboard = build_keyboard(buttons, layout) if buttons else None
        msg_parse_mode = call.data.get("parse_mode", parse_mode)
        caption = call.data.get("caption")
        
        url = call.data.get("url")
        file_path = call.data.get("file")
        
        for chat_id in chat_ids:
            result = await bot.send_video(
                chat_id=chat_id,
                video_url=url,
                video_path=file_path,
                caption=caption,
                parse_mode=msg_parse_mode,
                inline_keyboard=inline_keyboard
            )
            
            if result.get("ok") and result.get("msgId"):
                event_data = {
                    "chat_id": chat_id,
                    "message_id": result["msgId"],
                }
                hass.bus.async_fire(EVENT_MESSAGE_SENT, event_data)
                async_dispatcher_send(hass, signal(entry.entry_id), EVENT_MESSAGE_SENT, event_data)
    
    async def edit_message(call: ServiceCall):
        """Edit a message."""
        chat_ids = _get_chat_ids_from_params(hass, entry, call, allowed_chats)
        if not chat_ids:
            _LOGGER.error("No valid target found (entity_id, chat_id, or default chat)")
            return
        
        chat_id = chat_ids[0]
        
        # Получаем message_id (может быть строкой-шаблоном или числом)
        message_id_raw = call.data["message_id"]
        try:
            message_id = int(message_id_raw)
        except (ValueError, TypeError):
            # Если не число, возможно это шаблон, который нужно обработать
            # Но в большинстве случаев это будет число из шаблона
            _LOGGER.error(f"Invalid message_id: {message_id_raw}")
            return
        
        buttons = call.data.get("buttons")
        layout = call.data.get("buttons_layout", "row")
        inline_keyboard = build_keyboard(buttons, layout) if buttons else None
        msg_parse_mode = call.data.get("parse_mode", parse_mode)
        
        await bot.edit_message(
            chat_id=chat_id,
            msg_id=message_id,
            text=call.data["message"],
            parse_mode=msg_parse_mode,
            inline_keyboard=inline_keyboard
        )
    
    async def delete_messages(call: ServiceCall):
        """Delete messages."""
        chat_ids = _get_chat_ids_from_params(hass, entry, call, allowed_chats)
        if not chat_ids:
            _LOGGER.error("No valid target found (entity_id, chat_id, or default chat)")
            return
        
        chat_id = chat_ids[0]
        
        await bot.delete_messages(
            chat_id=chat_id,
            msg_ids=call.data["message_ids"]
        )
    
    async def answer_callback(call: ServiceCall):
        """Answer a callback query."""
        await bot.answer_callback(
            query_id=call.data["query_id"],
            text=call.data.get("text"),
            show_alert=call.data.get("show_alert", False),
            url=call.data.get("url")
        )
    
    # Register services
    hass.services.async_register(DOMAIN, "send_message", send_message, schema=SERVICE_SEND_MESSAGE_SCHEMA)
    hass.services.async_register(DOMAIN, "send_photo", send_photo, schema=SERVICE_SEND_PHOTO_SCHEMA)
    hass.services.async_register(DOMAIN, "send_video", send_video, schema=SERVICE_SEND_VIDEO_SCHEMA)
    hass.services.async_register(DOMAIN, "edit_message", edit_message, schema=SERVICE_EDIT_MESSAGE_SCHEMA)
    hass.services.async_register(DOMAIN, "delete_messages", delete_messages, schema=SERVICE_DELETE_MESSAGES_SCHEMA)
    hass.services.async_register(DOMAIN, "answer_callback", answer_callback, schema=SERVICE_ANSWER_CALLBACK_SCHEMA)
    
    # Forward entry setups for event and notify platforms
    await hass.config_entries.async_forward_entry_setups(entry, ["event", "notify"])
    
    entry.async_on_unload(entry.add_update_listener(async_update_listener))
    
    _LOGGER.info("VK Teams integration setup complete")
    return True


async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle config entry update."""
    _LOGGER.info("VK Teams config entry updated, reloading notify platform")
    await hass.config_entries.async_forward_entry_unload(entry, "notify")
    await hass.config_entries.async_forward_entry_setups(entry, ["notify"])


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloading VK Teams integration")
    
    await hass.config_entries.async_forward_entry_unload(entry, "event")
    await hass.config_entries.async_forward_entry_unload(entry, "notify")
    
    if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        bot = hass.data[DOMAIN][entry.entry_id].get("bot")
        if bot:
            await bot.stop_polling()
        hass.data[DOMAIN].pop(entry.entry_id, None)
    
    services = ["send_message", "send_photo", "send_video", "edit_message", "delete_messages", "answer_callback"]
    for service in services:
        hass.services.async_remove(DOMAIN, service)
    
    return True
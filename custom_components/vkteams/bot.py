"""VK Teams Bot API implementation."""

import logging
import json
import aiohttp
import asyncio
from typing import Optional, List, Dict, Any, Callable

from .const import (
    API_BASE, API_SEND_TEXT, API_SEND_FILE, API_EDIT_TEXT,
    API_DELETE_MESSAGES, API_ANSWER_CALLBACK, API_EVENTS_GET
)

_LOGGER = logging.getLogger(__name__)


class VKTeamsBot:
    """VK Teams Bot API wrapper."""

    def __init__(self, token: str, api_url: str):
        """Initialize the bot."""
        self.token = token
        self.api_url = api_url.rstrip("/")
        self.base_url = f"{self.api_url}{API_BASE}"
        self._polling_task = None
        self._polling_active = False
        self._last_event_id = 0
        self._callback_handler = None
        _LOGGER.info(f"Bot initialized with URL: {self.base_url}")

    async def _request_get(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """GET request with query parameters."""
        url = f"{self.base_url}{endpoint}"
        if params is None:
            params = {}
        params["token"] = self.token
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                result = await resp.json()
                _LOGGER.debug(f"GET {endpoint}: {result}")
                return result

    async def _request_post_form(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        """POST request with form-data (x-www-form-urlencoded)."""
        url = f"{self.base_url}{endpoint}"
        data["token"] = self.token
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as resp:
                result = await resp.json()
                _LOGGER.debug(f"POST Form {endpoint}: {result}")
                return result

    async def _request_post_file(self, endpoint: str, data: Dict, file_data: bytes, filename: str) -> Dict[str, Any]:
        """POST request with file upload (multipart/form-data)."""
        url = f"{self.base_url}{endpoint}"
        
        form = aiohttp.FormData()
        form.add_field("token", self.token)
        for key, value in data.items():
            form.add_field(key, value)
        form.add_field("file", file_data, filename=filename)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=form) as resp:
                result = await resp.json()
                _LOGGER.debug(f"POST File {endpoint}: {result}")
                return result

    # ========== ОСНОВНЫЕ МЕТОДЫ ==========

    async def send_text(
        self, 
        chat_id: str, 
        text: str, 
        parse_mode: str = None,
        reply_msg_id: List[int] = None,
        forward_chat_id: str = None,
        forward_msg_id: List[int] = None,
        inline_keyboard: List[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Send text message via /messages/sendText."""
        
        if inline_keyboard:
            data = {
                "chatId": chat_id,
                "text": text,
                "inlineKeyboardMarkup": json.dumps(inline_keyboard)
            }
            if parse_mode:
                data["parseMode"] = parse_mode
            if reply_msg_id:
                data["replyMsgId"] = reply_msg_id
            if forward_chat_id and forward_msg_id:
                data["forwardChatId"] = forward_chat_id
                data["forwardMsgId"] = forward_msg_id
            
            return await self._request_post_form(API_SEND_TEXT, data)
        
        params = {"chatId": chat_id, "text": text}
        if parse_mode:
            params["parseMode"] = parse_mode
        if reply_msg_id:
            params["replyMsgId"] = reply_msg_id
        if forward_chat_id and forward_msg_id:
            params["forwardChatId"] = forward_chat_id
            params["forwardMsgId"] = forward_msg_id
        
        return await self._request_get(API_SEND_TEXT, params)

    async def send_file(
        self,
        chat_id: str,
        file_url: str = None,
        file_path: str = None,
        file_data: bytes = None,
        filename: str = None,
        file_id: str = None,
        caption: str = None,
        parse_mode: str = None,
        reply_msg_id: List[int] = None,
        inline_keyboard: List[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Send file via /messages/sendFile."""
        
        # Если указан локальный путь к файлу
        if file_path and not file_data:
            try:
                with open(file_path, "rb") as f:
                    file_data = f.read()
                    filename = filename or file_path.split("/")[-1] or "file.bin"
            except Exception as e:
                _LOGGER.error(f"Failed to read local file {file_path}: {e}")
                return {"ok": False, "description": f"Failed to read local file: {e}"}
        
        # Если указан URL
        if file_url and not file_data:
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as resp:
                    if resp.status != 200:
                        return {"ok": False, "description": f"Failed to download: {file_url}"}
                    file_data = await resp.read()
                    filename = filename or file_url.split("/")[-1] or "file.bin"
        
        # Если есть inline_keyboard и file_id
        if inline_keyboard and file_id:
            data = {
                "chatId": chat_id,
                "fileId": file_id,
                "inlineKeyboardMarkup": json.dumps(inline_keyboard)
            }
            if caption:
                data["caption"] = caption
            if parse_mode:
                data["parseMode"] = parse_mode
            return await self._request_post_form(API_SEND_FILE, data)
        
        # Если есть file_data
        if file_data:
            data = {"chatId": chat_id}
            if caption:
                data["caption"] = caption
            if parse_mode:
                data["parseMode"] = parse_mode
            return await self._request_post_file(API_SEND_FILE, data, file_data, filename)
        
        # Если есть file_id
        params = {"chatId": chat_id}
        if file_id:
            params["fileId"] = file_id
        if caption:
            params["caption"] = caption
        if parse_mode:
            params["parseMode"] = parse_mode
        if reply_msg_id:
            params["replyMsgId"] = reply_msg_id
        
        return await self._request_get(API_SEND_FILE, params)

    async def send_photo(self, chat_id: str, photo_url: str = None, photo_path: str = None, caption: str = None, **kwargs) -> Dict[str, Any]:
        """Send a photo via /messages/sendFile."""
        return await self.send_file(chat_id, file_url=photo_url, file_path=photo_path, caption=caption, **kwargs)

    async def send_video(self, chat_id: str, video_url: str = None, video_path: str = None, caption: str = None, **kwargs) -> Dict[str, Any]:
        """Send a video via /messages/sendFile."""
        return await self.send_file(chat_id, file_url=video_url, file_path=video_path, caption=caption, **kwargs)

    async def edit_message(
        self,
        chat_id: str,
        msg_id: int,
        text: str,
        parse_mode: str = None,
        inline_keyboard: List[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Edit message via /messages/editText."""
        
        if inline_keyboard:
            data = {
                "chatId": chat_id,
                "msgId": msg_id,
                "text": text,
                "inlineKeyboardMarkup": json.dumps(inline_keyboard)
            }
            if parse_mode:
                data["parseMode"] = parse_mode
            return await self._request_post_form(API_EDIT_TEXT, data)
        
        params = {"chatId": chat_id, "msgId": msg_id, "text": text}
        if parse_mode:
            params["parseMode"] = parse_mode
        return await self._request_get(API_EDIT_TEXT, params)

    async def delete_messages(self, chat_id: str, msg_ids: List[int]) -> Dict[str, Any]:
        """Delete messages via /messages/deleteMessages."""
        params = {"chatId": chat_id, "msgId": ",".join(str(mid) for mid in msg_ids)}
        result = await self._request_get(API_DELETE_MESSAGES, params)
        _LOGGER.info(f"Delete messages result for {msg_ids}: {result}")
        return result

    async def answer_callback(
        self,
        query_id: str,
        text: str = None,
        show_alert: bool = False,
        url: str = None
    ) -> Dict[str, Any]:
        """Answer callback query via /messages/answerCallbackQuery."""
        params = {
            "queryId": query_id,
            "showAlert": str(show_alert).lower()
        }
        if text:
            params["text"] = text
        if url:
            params["url"] = url
        return await self._request_get(API_ANSWER_CALLBACK, params)

    # ========== LONG POLLING ==========

    async def get_events(self, poll_time: int = 30, last_event_id: int = 0) -> Dict[str, Any]:
        """Get events via /events/get."""
        params = {
            "pollTime": min(poll_time, 60),
            "lastEventId": last_event_id
        }
        return await self._request_get(API_EVENTS_GET, params)

    async def start_polling(self, callback_handler: Callable, poll_time: int = 30):
        """Start long polling loop."""
        self._polling_active = True
        self._callback_handler = callback_handler
        self._polling_task = asyncio.create_task(self._polling_loop(poll_time))
        _LOGGER.info("Long polling started")

    async def _polling_loop(self, poll_time: int):
        """Internal polling loop."""
        while self._polling_active:
            try:
                result = await self.get_events(poll_time, self._last_event_id)
                
                if result.get("ok") and result.get("events"):
                    for event in result["events"]:
                        event_id = event.get("eventId")
                        if event_id is not None:
                            self._last_event_id = event_id + 1
                        
                        if self._callback_handler:
                            try:
                                await self._callback_handler(event)
                            except Exception as e:
                                _LOGGER.error(f"Error in callback handler: {e}")
                elif not result.get("ok"):
                    await asyncio.sleep(5)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                _LOGGER.error(f"Polling loop error: {e}")
                await asyncio.sleep(5)

    async def stop_polling(self):
        """Stop long polling."""
        self._polling_active = False
        if self._polling_task:
            self._polling_task.cancel()
            try:
                await self._polling_task
            except asyncio.CancelledError:
                pass
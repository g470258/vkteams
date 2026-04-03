"""Constants for VK Teams integration."""

DOMAIN = "vkteams"
CONF_TOKEN = "token"
CONF_API_URL = "api_url"
CONF_CHAT_ID = "chat_id"
CONF_ALLOWED_CHAT_IDS = "allowed_chat_ids"
CONF_PARSE_MODE = "parse_mode"
CONF_POLL_INTERVAL = "poll_interval"

DEFAULT_API_URL = "https://myteam.mail.ru"
DEFAULT_PARSE_MODE = "HTML"
DEFAULT_POLL_INTERVAL = 30

PARSE_MODES = ["HTML", "MarkdownV2"]

# Subentry types
SUBENTRY_TYPE_ALLOWED_CHAT_IDS = "allowed_chat_ids"

# API endpoints
API_BASE = "/bot/v1"
API_SEND_TEXT = "/messages/sendText"
API_SEND_FILE = "/messages/sendFile"
API_EDIT_TEXT = "/messages/editText"
API_DELETE_MESSAGES = "/messages/deleteMessages"
API_ANSWER_CALLBACK = "/messages/answerCallbackQuery"
API_EVENTS_GET = "/events/get"
API_SELF_GET = "/self/get"

# Button styles
BUTTON_STYLE_DEFAULT = "default"
BUTTON_STYLE_PRIMARY = "primary"
BUTTON_STYLE_SECONDARY = "secondary"
BUTTON_STYLE_DANGER = "danger"

# Event types
EVENT_CALLBACK = "vkteams_callback"
EVENT_COMMAND = "vkteams_command"
EVENT_TEXT = "vkteams_text"
EVENT_MESSAGE_SENT = "vkteams_sent"

# Signal for dispatcher
SIGNAL_UPDATE_EVENT = "vkteams_update_event"

# Subentry types
SUBENTRY_TYPE_ALLOWED_CHAT_IDS = "allowed_chat_ids"

# Service names (обновлённые)
SERVICE_SEND_MESSAGE = "send_message"
SERVICE_SEND_PHOTO = "send_photo"
SERVICE_SEND_VIDEO = "send_video"
SERVICE_EDIT_MESSAGE = "edit_message"
SERVICE_DELETE_MESSAGES = "delete_messages"
SERVICE_ANSWER_CALLBACK = "answer_callback"

# Event attributes
ATTR_ARGS = "args"
ATTR_CALLBACK_DATA = "callback_data"
ATTR_CHAT_ID = "chat_id"
ATTR_CHAT_INSTANCE = "chat_instance"
ATTR_COMMAND = "command"
ATTR_DATA = "data"
ATTR_DATE = "date"
ATTR_EVENT_TYPE = "event_type"
ATTR_FILE_ID = "file_id"
ATTR_FILE_NAME = "file_name"
ATTR_FILE_SIZE = "file_size"
ATTR_FROM_FIRST = "from_first"
ATTR_FROM_LAST = "from_last"
ATTR_ID = "id"
ATTR_MESSAGE = "message"
ATTR_MESSAGE_ID = "message_id"
ATTR_TEXT = "text"
ATTR_USER_ID = "user_id"
ATTR_BOT = "bot"
ATTR_TITLE = "title"
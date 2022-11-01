import logging
from aiogram import Bot
from decouple import config
from aiogram.types import ChatMemberAdministrator

from utils.files import convert_txt_files_to_json, dump_json

__all__ = [
    "get_admin_id",
    "check_bot_permisions",
    "create_config",
    "create_json_banlist",
    "create_loggers",
]


async def get_admins_id(bot: Bot, chat_id: str = config("CHAT_ID")) -> list:
    """Return list of admins id from chat"""

    admins = await bot.get_chat_administrators(chat_id)
    return [admin.user.id for admin in admins]


async def check_bot_permisions(bot: Bot, chat_id: str = config("CHAT_ID")) -> None:
    """Check bot permissions in chat"""

    bot_info = await bot.get_chat_member(chat_id, bot.id)

    # Check if bot is admin
    if not isinstance(bot_info, ChatMemberAdministrator):
        info_logger = logging.getLogger("info_logger")
        info_logger.error(
            f"Chat id: {chat_id}. Exception: PermissionError. Bot is not admin in this chat"
        )
        raise PermissionError("Bot is not admin in this chat")

    # Check if bot can delete and restrict messages
    if not bot_info.can_delete_messages or not bot_info.can_restrict_members:
        info_logger = logging.getLogger("info_logger")
        info_logger.error(
            f"Chat id: {chat_id}. Exception: PermissionError. Bot need permissions to delete messages and restrict members"
        )
        raise PermissionError(
            "Bot need permissions to delete messages and restrict members"
        )


async def create_config() -> None:
    """Create empty config file"""

    cfg = {
        "admins": [],
        "silent_ban_users": {"id": [], "username": [], "fullname": []},
    }
    await dump_json(config("JSON_CONFIG_PATH"), "w", cfg)


async def create_json_banlist() -> None:
    """Create json banlist with words from txt files"""

    await convert_txt_files_to_json(
        config("JSON_BANWORD_PATH"),
        config("TXT_BANWORD_PATH"),
        config("CUSTOM_TXT_BANWORD_PATH"),
    )


async def create_loggers() -> None:
    """Register and start loggers"""

    # Create formatter for handlers
    fmt = "%(asctime)s %(filename)-18s %(levelname)-8s: %(message)s"
    fmt_date = "%Y-%m-%d %H:%M:%S %Z"
    formatter = logging.Formatter(fmt, fmt_date)

    # Register message logger
    message_logger = logging.getLogger("message_logger")
    message_logger.setLevel(logging.DEBUG)

    # Create file handler for message logger
    message_handler = logging.FileHandler(
        encoding="utf-8", filename=config("MESSAGE_LOG_PATH")
    )
    message_handler.setLevel(logging.DEBUG)

    # Add formatter to handler
    message_handler.setFormatter(formatter)
    message_logger.addHandler(message_handler)

    # Register info logger
    info_logger = logging.getLogger("info_logger")
    info_logger.setLevel(logging.INFO)

    # Create file handler for info logger
    info_handler = logging.FileHandler(
        encoding="utf-8", filename=config("INFO_LOG_PATH")
    )
    info_handler.setLevel(logging.INFO)

    # Add formatter to handler
    info_handler.setFormatter(formatter)
    info_logger.addHandler(info_handler)

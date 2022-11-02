import logging
from aiogram import types
from utils.files import get_admins_from_config

__all__ = ["log_message", "admin_required"]


def log_message(func):
    """Decorator to log message"""

    async def wrapper(*args, **kwargs):
        message: types.Message = args[0]

        message_logger = logging.getLogger("message_logger")
        message_logger.debug(f"Message: {message}")
        await func(*args, **kwargs)

    return wrapper


def non_bot_required(func):
    """Decorator to check if user is not bot"""

    async def wrapper(*args, **kwargs):
        message: types.Message = args[0]

        if message.from_user.is_bot:
            info_logger = logging.getLogger("info_logger")
            info_logger.info(
                f"Bot with id {message.from_user.id} wrote a message in Chat id: {message.chat.id}, skip it. Message id: {message.message_id}"
            )
            return
        return await func(*args, **kwargs)

    return wrapper


def admin_required(func):
    """Decorator to check if user is admin"""

    async def wrapper(*args, **kwargs):
        message: types.Message = args[0]

        admins_list = await get_admins_from_config()
        if message.from_user.id not in admins_list:

            info_logger = logging.getLogger("info_logger")
            info_logger.info(
                f"Non admin with id {message.from_user.id} tried to use admin command in Chat id {message.chat.id}. Message id: {message.message_id}"
            )

            return await message.answer(f"{message.from_user.first_name}, ты не админ!")

        return await func(*args, **kwargs)

    return wrapper


def private_chat_only(func):
    """Decorator to check if user writes in private chat"""

    async def wrapper(*args, **kwargs):
        message: types.Message = args[0]

        if message.chat.type != types.ChatType.PRIVATE:

            info_logger = logging.getLogger("info_logger")
            info_logger.info(
                f"User with id {message.from_user.id} tried to use private command in group chat with id: {message.chat.id}. Message id: {message.message_id}"
            )
            return await message.answer(
                f"{message.from_user.first_name}, я не обрабатываю личные сообщения в группах!"
            )
        return await func(*args, **kwargs)

    return wrapper

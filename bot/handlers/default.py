import logging

from aiogram import Dispatcher, types

from utils.default import filter_obscene_words, is_user_banned

__all__ = ["register_default_handlers"]


# @log_message
async def message_processing(message: types.Message):
    """Handle all non-admin messages"""

    message_logger = logging.getLogger("message_logger")
    message_logger.debug(f"Message: {message}")

    if await is_user_banned(message):
        await message.delete()
        return
    await filter_obscene_words(message)


def register_default_handlers(dp: Dispatcher):
    """Register default handlers"""

    dp.register_message_handler(message_processing)

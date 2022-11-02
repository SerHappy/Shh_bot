from aiogram import Dispatcher, types
from utils.decorators import log_message

from utils.default import filter_obscene_words, is_user_banned

__all__ = ["register_default_handlers"]


@log_message
async def message_processing(message: types.Message, **kwargs):
    """Handle all non-admin messages"""

    if await is_user_banned(message):
        await message.delete()
        return
    await filter_obscene_words(message)


def register_default_handlers(dp: Dispatcher):
    """Register default handlers"""

    dp.register_message_handler(message_processing)

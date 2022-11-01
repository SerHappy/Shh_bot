import string
import logging

from aiogram import types
from decouple import config

from utils.decorators import non_bot_required
from utils.admin import get_silent_ban_dict
from utils.files import get_admins_from_config, get_json


__all__ = ["is_user_banned", "filter_obscene_words"]


async def is_user_banned(user_message: types.Message) -> bool:
    """Check if user is banned"""

    info_logger = logging.getLogger("info_logger")

    # Get dict of 'silent_ban_users' key
    silent_ban_users = await get_silent_ban_dict()

    try:

        # Check if user is banned by id
        if "id" in user_message["from"]:
            if user_message.from_user.id in silent_ban_users["id"]:
                info_logger.info(
                    f"User with id {user_message.from_user.id} is banned by id. Message with id: {user_message.message_id} in Chat id: {user_message.chat.id}was deleted"
                )
                return True

        # Check if user is banned by username
        if "username" in user_message["from"]:
            if user_message.from_user.username.lower() in silent_ban_users["username"]:
                info_logger.info(
                    f"User with id {user_message.from_user.id} is banned by username. Message with id: {user_message.message_id} in Chat id: {user_message.chat.id} was deleted"
                )
                return True

        # Check if user is banned by fullname
        if "full_name" in user_message["from"]:
            if user_message.from_user.full_name.lower() in silent_ban_users["fullname"]:
                info_logger.info(
                    f"User with id {user_message.from_user.id} is banned by id. Message with id: {user_message.message_id} in Chat id: {user_message.chat.id} was deleted"
                )
                return True

    except TypeError:
        info_logger.error(
            f"Message id: {user_message.message_id}, Chat id: {user_message.chat.id}. Something wrong with user_message: {user_message}"
        )
        return False
    return False


@non_bot_required
async def filter_obscene_words(message: types.Message) -> None:
    """Filter obscene words"""

    info_logger = logging.getLogger("info_logger")

    admins_list = await get_admins_from_config()

    # If user is admin, don't filter his message
    if message.from_user.id in admins_list:
        info_logger.info(
            f"Message with id: {message.message_id} in Chat id: {message.chat.id} from admin, skip filter"
        )
        return

    # Get obscene words from config
    badWords = await get_json(config("JSON_BANWORD_PATH"))

    # Compare message text with obscene words
    if {
        word.lower().translate(str.maketrans("", "", string.punctuation))
        for word in message.text.split(" ")
    }.intersection(set(badWords)) != set():

        # If obscene words found, delete message
        info_logger.info(
            f"Message with id: {message.message_id} in Chat id: {message.chat.id} was deleted by filter"
        )
        await message.reply(f"{message.from_user.first_name}, тут такое запрещено!")
        await message.delete()

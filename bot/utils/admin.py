import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from decouple import config

from utils.files import dump_json, get_json, get_txt

__all__ = [
    "get_silent_ban_dict",
    "delete_all_silent_ban_users",
    "silent_ban_user_by_id",
    "silent_ban_user_by_username",
    "silent_ban_user_by_fullname",
    "silent_unban_user_by_id",
    "silent_unban_user_by_username",
    "silent_unban_user_by_fullname",
    "finish_fsm",
]


async def _silent_ban_user(
    var_to_ban: int | str, dict_key_name: str, message: types.Message
) -> None:
    """Private function to ban user by id, username or fullname"""

    # Get dict of 'silent_ban_users' key
    silent_ban_dict = await get_silent_ban_dict()
    # Get dict of 'dict_key_name' key
    silent_ban_key_dict = silent_ban_dict[dict_key_name]
    # If user is not in dict, add him
    if var_to_ban not in silent_ban_key_dict:
        silent_ban_key_dict.append(var_to_ban)

        cfg = await get_json(config("JSON_CONFIG_PATH"))
        cfg["silent_ban_users"][dict_key_name] = silent_ban_key_dict

        await dump_json(config("JSON_CONFIG_PATH"), "w", cfg)

        info_lgger = logging.getLogger("info_logger")
        info_lgger.info(
            f"Admin with id {message.from_user.id} successfully banned User with {dict_key_name} <{var_to_ban}>"
        )

        await message.answer(
            f"Пользователь с {dict_key_name} <{var_to_ban}> успешно забанен"
        )
    else:
        info_lgger = logging.getLogger("info_logger")
        info_lgger.warning(
            f"Admin with id {message.from_user.id} tried to ban user with {dict_key_name} <{var_to_ban}>, but user is already banned"
        )

        await message.answer(
            f"Пользователь с {dict_key_name} <{var_to_ban}> уже забанен"
        )


async def _silent_unban_user(
    var_to_unban: int | str, dict_key_name: str, message: types.Message
) -> None:
    """Private function to unban user by id, username or fullname"""

    # Get dict of 'silent_ban_users' key
    silent_ban_dict = await get_silent_ban_dict()
    # Get dict of 'dict_key_name' key
    silent_ban_key_dict = silent_ban_dict[dict_key_name]
    # If user is in dict, delete him
    if var_to_unban in silent_ban_key_dict:
        silent_ban_key_dict.remove(var_to_unban)

        cfg = await get_json(config("JSON_CONFIG_PATH"))
        cfg["silent_ban_users"][dict_key_name] = silent_ban_key_dict

        await dump_json(config("JSON_CONFIG_PATH"), "w", cfg)

        info_lgger = logging.getLogger("info_logger")
        info_lgger.info(
            f"Admin with id {message.from_user.id} successfully unbanned User with {dict_key_name} <{var_to_unban}>"
        )

        await message.answer(
            f"Пользователь с {dict_key_name} <{var_to_unban}> успешно разбанен"
        )
    else:
        info_lgger = logging.getLogger("info_logger")
        info_lgger.warning(
            f"Admin with id {message.from_user.id} tried to unban user with {dict_key_name} <{var_to_unban}>, but user is not banned"
        )

        await message.answer(
            f"Пользователь с {dict_key_name} <{var_to_unban}> не забанен"
        )


async def finish_fsm(state=FSMContext) -> None:
    """Cansels current state"""

    current_state = await state.get_state()
    if current_state is not None:

        info_lgger = logging.getLogger("info_logger")
        info_lgger.debug(f"State {current_state} is finished")

        await state.finish()

async def delete_custom_banword(banword: str, message: types.Message) -> None:
    """Deletes custom banword"""

    # Get list if custom banwords
    custom_banwords_dict = await get_txt(config("CUSTOM_TXT_BANWORD_PATH"))

    # If banword is in dict, delete it
    if banword in custom_banwords_dict:
        custom_banwords_dict.remove(banword)

        cfg = await get_json(config("JSON_CONFIG_PATH"))
        cfg["custom_banwords"] = custom_banwords_dict

        await dump_json(config("JSON_CONFIG_PATH"), "w", cfg)

        info_lgger = logging.getLogger("info_logger")
        info_lgger.info(
            f"Admin with id {message.from_user.id} successfully deleted custom banword <{banword}>"
        )

        await message.answer(f"Запрещенное слово <{banword}> успешно удалено")
    else:
        info_lgger = logging.getLogger("info_logger")
        info_lgger.warning(
            f"Admin with id {message.from_user.id} tried to delete custom banword <{banword}>, but banword is not in custom banwords list"
        )

        await message.answer(f"Запрещенное слово <{banword}> не найдено")


async def get_silent_ban_dict() -> dict:
    """Returns dict with silent ban users"""

    cfg = await get_json(config("JSON_CONFIG_PATH"))
    return cfg["silent_ban_users"] if "silent_ban_users" in cfg.keys() else {}


async def silent_ban_user_by_username(username: str, message: types.Message) -> None:
    """Bans user by username"""

    await _silent_ban_user(username, "username", message)


async def silent_ban_user_by_id(user_id: int, message: types.Message) -> None:
    """Bans user by id"""

    await _silent_ban_user(user_id, "id", message)


async def silent_ban_user_by_fullname(fullname: list, message: types.Message) -> None:
    """Bans user by fullname"""

    fullname = " ".join(fullname)
    await _silent_ban_user(fullname, "fullname", message)


async def silent_unban_user_by_username(username: str, message: types.Message) -> None:
    """Unbans user by username"""

    await _silent_unban_user(username, "username", message)


async def silent_unban_user_by_id(user_id: int, message: types.Message) -> None:
    """Unbans user by id"""

    await _silent_unban_user(user_id, "id", message)


async def silent_unban_user_by_fullname(fullname: list, message: types.Message) -> None:
    """Unbans user by fullname"""

    fullname = " ".join(fullname)
    await _silent_unban_user(fullname, "fullname", message)


async def delete_all_silent_ban_users(message: types.Message) -> None:
    """Deletes all silent ban users"""

    cfg = await get_json(config("JSON_CONFIG_PATH"))
    cfg["silent_ban_users"] = {"id": [], "username": [], "first_name": []}

    await dump_json(config("JSON_CONFIG_PATH"), "w", cfg)

    info_lgger = logging.getLogger("info_logger")
    info_lgger.debug(f"All silent ban users were deleted")

    await message.answer("Список забаненных пользователей очищен")

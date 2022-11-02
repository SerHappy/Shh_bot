import logging

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from decouple import config

from states.admin.states import FSM_Admin_word, FSM_Admin_silent_ban

from utils.decorators import admin_required, log_message, private_chat_only
from utils.files import (
    add_word_to_file,
    create_txt_file,
    get_txt,
    update_json_banlist,
)
from utils.admin import (
    delete_all_silent_ban_users,
    get_silent_ban_dict,
    silent_ban_user_by_fullname,
    silent_ban_user_by_id,
    silent_ban_user_by_username,
    finish_fsm,
    silent_unban_user_by_fullname,
    silent_unban_user_by_id,
    silent_unban_user_by_username,
)

__all__ = ["register_admin_handlers"]


@log_message
@private_chat_only
@admin_required
async def admin_fsm_words_start(message: types.Message, **kwargs) -> None:
    """Start admin FSM for add banwords"""

    await message.answer(
        "Выберите действие\n1. Вывести пользовательские слова\n2. Добавить слово\n3. Удалить слово"
    )
    await FSM_Admin_word.value.set()


@log_message
async def check_value_word(message: types.Message, **kwargs) -> None:
    """Check value for admin add word FSM"""

    if message.text == "1":
        await FSM_Admin_word.print_custom_banwords.set()
        await print_custom_banwords(message, **kwargs)
    elif message.text == "2":
        await message.answer(f"Введите слово для добавления")
        await FSM_Admin_word.add_custom_banword.set()
    elif message.text == "3":
        await message.answer(f"Введите слово для удаления")
        await FSM_Admin_word.delete_custom_banword.set()
    else:
        await message.answer(f"Неверное значение")


@log_message
async def add_ban_word(message: types.Message, **kwargs) -> None:
    """Add ban word to json banword"""

    state = kwargs["state"]

    await add_word_to_file(config("CUSTOM_TXT_BANWORD_PATH"), message.text)
    await update_json_banlist()
    await message.answer(f"Cлово {message.text} добавлено в бан-лист")
    await finish_fsm(state)


@log_message
async def delete_ban_word(message: types.Message, **kwargs) -> None:
    """Delete ban word from json banword"""

    state = kwargs["state"]

    find = False
    words = await get_txt(config("CUSTOM_TXT_BANWORD_PATH"))
    for word in words:
        if message.text == word:
            find = True
            words.remove(word)
            await create_txt_file(config("CUSTOM_TXT_BANWORD_PATH"), words)
            await message.answer(f"Cлово {message.text} было удалено из бан-листа")
    if find == False:
        await message.answer(f"Cлово {message.text} не найдено в бан-листе")
    await finish_fsm(state)


async def print_custom_banwords(message: types.Message, **kwargs) -> None:
    """Print add banwords"""

    state = kwargs["state"]

    banWords = await get_txt(config("CUSTOM_TXT_BANWORD_PATH"))
    await message.answer(f"Добавленные слова:\n{', '.join(i for i in banWords)}")
    await finish_fsm(state)


@log_message
@private_chat_only
@admin_required
async def admin_fsm_silent_ban_start(message: types.Message, **kwargs) -> None:
    """Start admin FSM for silent ban"""

    await message.answer(
        "Выберите действие\n1. Забанить пользователя\n2. Разбанить пользователя\n3. Очистить список забаненных пользователей\n4. Вывести список забаненых пользователей"
    )
    await FSM_Admin_silent_ban.value.set()


@log_message
async def check_value_silent_ban(message: types.Message, **kwargs) -> None:
    """Check value for admin silent ban FSM"""

    state = kwargs["state"]

    if message.text == "1":
        await message.answer(
            f"{message.from_user.first_name}, введи один из трех шаблонов для бана пользователя!\n1. username: @username\n2. id: 123456789\n3. name: Fullname\n"
        )
        await FSM_Admin_silent_ban.silent_ban.set()
    elif message.text == "2":
        await message.answer(
            f"{message.from_user.first_name}, введи один из трех шаблонов для разбана пользователя!\n1. username: @username\n2. id: 123456789\n3. name: Fullname\n"
        )
        await FSM_Admin_silent_ban.silent_unban.set()
    elif message.text == "3":
        await FSM_Admin_silent_ban.clear_silent_ban_users.set()
        await clear_silent_ban_users(message, **kwargs)
    elif message.text == "4":
        await FSM_Admin_silent_ban.print_silent_ban_users.set()
        await print_silent_ban_users(message, **kwargs)
    else:
        await message.answer(f"Неверное значение")


@log_message
async def silent_ban_user(message: types.Message, **kwargs) -> None:
    """Hander to add user to silent ban by id,username or fullname"""

    state = kwargs["state"]

    info_logger = logging.getLogger("info_logger")

    # Get template and variable list from message
    try:
        template, *lst = list(
            filter(
                lambda x: x != "",
                map(lambda x: x.strip().lower(), message.text.split(":")),
            )
        )
        variable_list = lst[0].split(" ")
    except (ValueError, IndexError):
        info_logger.error(
            f"Message id:{message.message_id}. Неверный шаблон для бана пользователя: {message.text}"
        )
        await message.answer("Неверный шаблон!")
        return

    # Match template and call function
    match template:
        case "username":
            try:
                if len(variable_list) > 1:
                    raise ValueError("Too many arguments")
                username = variable_list[0]
                username = username[1:] if username.startswith("@") else username
                await silent_ban_user_by_username(username, message)
            except (IndexError, ValueError) as e:
                info_logger.error(
                    f"Message id:{message.message_id}. Неверный username для бана пользователя: {message.text}"
                )
                await message.answer(f"Неверный username\nException: {e}")
                return
        case "id":
            try:
                if len(variable_list) > 1:
                    raise ValueError("Too many arguments")
                user_id = int(variable_list[0])
                await silent_ban_user_by_id(user_id, message)
            except ValueError as e:
                info_logger.error(
                    f"Message id:{message.message_id}. Неверный id для бана пользователя: {message.text}"
                )
                await message.answer(f"Неверный тип параметра id\nException: {e}")
                return
        case "name":
            try:
                if len(variable_list) == 0:
                    raise ValueError("Empty name")
                fullname = variable_list
                await silent_ban_user_by_fullname(fullname, message)
            except ValueError as e:
                info_logger.error(
                    f"Message id:{message.message_id}. Неверное имя для бана пользователя: {message.text}"
                )
                await message.answer(f"Неверный тип параметра fullname\nException: {e}")
                return
        case _:
            await message.answer("Неверный шаблон!")
            return
    await finish_fsm(state)


@log_message
async def silent_unban_user(message: types.Message, **kwargs) -> None:
    """Hander for silent unban user by id, username or fullname"""

    state = kwargs["state"]

    info_logger = logging.getLogger("info_logger")

    # Get template and variable list from message
    try:
        template, *lst = list(
            filter(
                lambda x: x != "",
                map(lambda x: x.strip().lower(), message.text.split(":")),
            )
        )
        variable_list = lst[0].split(" ")
    except (ValueError, IndexError):
        info_logger.error(
            f"Message id:{message.message_id}. Неверный шаблон для разбана пользователя: {message.text}"
        )
        await message.answer("Неверный шаблон!")
        return

    # Match template and call function
    match template:
        case "username":
            try:
                if len(variable_list) > 1:
                    raise ValueError("Too many arguments")
                username = variable_list[0]
                username = username[1:] if username.startswith("@") else username
                await silent_unban_user_by_username(username, message)
            except (IndexError, ValueError) as e:
                info_logger.error(
                    f"Message id:{message.message_id}. Неверный username для разбана пользователя: {message.text}"
                )
                await message.answer(f"Неверный username\nException: {e}")
                return
        case "id":
            try:
                if len(variable_list) > 1:
                    raise ValueError("Too many arguments")
                user_id = int(variable_list[0])
                await silent_unban_user_by_id(user_id, message)
            except ValueError as e:
                info_logger.error(
                    f"Message id:{message.message_id}. Неверный id для разбана пользователя: {message.text}"
                )
                await message.answer(f"Неверный тип параметра id\nException: {e}")
                return
        case "name":
            try:
                if len(variable_list) == 0:
                    raise ValueError("Empty name")
                fullname = variable_list
                await silent_unban_user_by_fullname(fullname, message)
            except ValueError as e:
                info_logger.error(
                    f"Message id:{message.message_id}. Неверное имя для разбана пользователя: {message.text}"
                )
                await message.answer(f"Неверный тип параметра fullname\nException: {e}")
                return
        case _:
            await message.answer("Неверный шаблон!")
            return

    # Finish FSM
    await finish_fsm(state)


async def clear_silent_ban_users(message: types.Message, **kwargs) -> None:
    """Hander for clear silent ban users"""

    state = kwargs["state"]

    await delete_all_silent_ban_users(message)
    await finish_fsm(state)


async def print_silent_ban_users(message: types.Message, **kwargs) -> None:
    """Hander for print silent ban users"""

    state = kwargs["state"]

    # Get dict of silent ban users
    users = await get_silent_ban_dict()

    # Create message
    msg = "Список забаненных пользователей:\n"
    for silent_ban_field in ["id", "username", "fullname"]:
        field_users = list(users[silent_ban_field])
        msg += f"{silent_ban_field}: {', '.join([str(i) for i in field_users]) if len(field_users) > 0 else 'Список пуст!'}\n"

    await message.answer(msg)
    await finish_fsm(state)


def register_admin_handlers(dp: Dispatcher) -> None:
    """Register admin handlers"""

    dp.register_message_handler(admin_fsm_words_start, commands=["word"], state="*")
    dp.register_message_handler(check_value_word, state=FSM_Admin_word.value)
    dp.register_message_handler(add_ban_word, state=FSM_Admin_word.add_custom_banword)
    dp.register_message_handler(
        delete_ban_word, state=FSM_Admin_word.delete_custom_banword
    )
    dp.register_message_handler(
        print_custom_banwords, state=FSM_Admin_word.print_custom_banwords
    )

    dp.register_message_handler(admin_fsm_silent_ban_start, commands=["ban"])
    dp.register_message_handler(
        check_value_silent_ban, state=FSM_Admin_silent_ban.value
    )
    dp.register_message_handler(silent_ban_user, state=FSM_Admin_silent_ban.silent_ban)
    dp.register_message_handler(
        silent_unban_user, state=FSM_Admin_silent_ban.silent_unban
    )
    dp.register_message_handler(
        print_silent_ban_users, state=FSM_Admin_silent_ban.print_silent_ban_users
    )

from aiogram.dispatcher.filters.state import State, StatesGroup

__all__ = ["FSM_Admin_word", "FSM_Admin_silent_ban"]


class FSM_Admin_word(StatesGroup):
    """Admin FSM for add custom ban word"""

    value = State()
    add_custom_banword: State = State()
    delete_custom_banword: State = State()
    print_custom_banwords: State = State()


class FSM_Admin_silent_ban(StatesGroup):
    """Admin FSM for silently ban user"""

    value = State()
    silent_ban: State = State()
    silent_unban: State = State()
    clear_silent_ban_users: State = State()
    print_silent_ban_users: State = State()

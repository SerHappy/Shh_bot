import asyncio
import logging
import nest_asyncio
import os

from aiogram import executor
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from decouple import config

from utils.files import load_admins_to_config
from utils.before_start import (
    check_bot_permisions,
    create_config,
    create_json_banlist,
    get_admins_id,
    create_loggers,
)
from handlers.admin import register_admin_handlers
from handlers.default import register_default_handlers



async def _on_startup(dp: Dispatcher) -> None:
    """Calls on bot start"""

    # Add startup message to info.log
    info_logger = logging.getLogger("info_logger")
    bot_info = await dp.bot.get_me()
    info_logger.info(f"Bot [@{bot_info.username}] started!")


async def _on_shutdown(dp: Dispatcher) -> None:
    """Calls on bot shutdown"""

    # Add shutdown message to info.log
    info_logger = logging.getLogger("info_logger")
    bot_info = await dp.bot.get_me()
    info_logger.info(f"Bot [@{bot_info.username}] stopped!")


async def main() -> None:
    """Main function"""

    # Define bot, storage and dp
    storage = MemoryStorage()
    bot = Bot(token=config("BOT_TOKEN", cast=str))
    dispatcher = Dispatcher(bot, storage=storage)

    # Check bot permissions
    try:
        await check_bot_permisions(bot)
    except (PermissionError) as e:
        try:
            await bot.send_message(
                config("CHAT_ID"), f"Error with bot permissions: {e}"
            )
        finally:
            info_logger = logging.getLogger("info_logger")
            info_logger.error(
                f"Chat id: {config('CHAT_ID')}. Error with bot permissions: {e}"
            )
            await bot.close()
            return

    # Check config exists
    if not os.path.exists(config("JSON_CONFIG_PATH")):
        # Create config and load admins to it
        await create_config()
        admins = await get_admins_id(bot)
        await load_admins_to_config(admins)

    # Create json banlist
    if not os.path.exists(config("JSON_BANWORD_PATH")):
        await create_json_banlist()

    # Register handlers
    # register_setup_handlers(dispatcher)
    register_admin_handlers(dispatcher)
    register_default_handlers(dispatcher)

    # Сreate loggers
    await create_loggers()

    # Start polling
    executor.start_polling(
        dispatcher, skip_updates=True, on_startup=_on_startup, on_shutdown=_on_shutdown
    )


if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())

import json
from typing import Any

from decouple import config

__all__ = [
    "dump_json",
    "get_json",
    "get_txt",
    "convert_txt_files_to_json",
    "create_txt_file",
    "add_word_to_file",
    "update_json_banlist",
    "load_admins_to_config",
    "get_admins_from_config",
]


async def dump_json(file_path: str, mode: str, args: Any) -> None:
    """Dump json to file"""

    with open(file_path, mode) as file:
        json.dump(args, file, indent=4, ensure_ascii=False)


async def get_json(file_path: str):
    """Get data from json file"""

    with open(file_path, "r") as file:
        return json.load(file)


async def get_txt(file_path: str) -> list:
    """Get list of all words from file"""

    with open(file_path, "r") as file:
        return [word.strip() for word in file.readlines() if word != ""]


async def convert_txt_files_to_json(
    json_path: str, *txt_pathes: tuple[str, ...]
) -> None:
    """Convert txt files to json"""

    badWordList = []
    for txtFile in txt_pathes:
        with open(txtFile, "r") as file:
            for word in file.readlines():
                if word != "":
                    badWordList.append(word.strip())
    await dump_json(json_path, "w", badWordList)


async def create_txt_file(file_path: str, list_of_words: list) -> None:
    """Create txt file with a given list of words"""

    with open(file_path, "w") as file:
        for word in list_of_words:
            file.write(word + "\n")


async def add_word_to_file(file_path: str, word: str) -> None:
    """Add word to file"""

    with open(file_path, "a") as file:
        file.write(word.lower() + "\n")


async def update_json_banlist() -> None:
    """Update json banlist"""

    await convert_txt_files_to_json(
        config("JSON_BANWORD_PATH"),
        config("TXT_BANWORD_PATH"),
        config("CUSTOM_TXT_BANWORD_PATH"),
    )


async def load_admins_to_config(admins_id: list) -> None:
    """Load list of admins id to config"""

    # Add telegram id to config
    admins_id.append(777000)

    dictionary = {"admins": admins_id}

    # Dump admins id to config
    cfg = await get_json(config("JSON_CONFIG_PATH"))
    cfg["admins"] = dictionary["admins"]

    await dump_json(config("JSON_CONFIG_PATH"), "w", cfg)


async def get_admins_from_config() -> list:
    """Get admins list from config"""

    data = await get_json(config("JSON_CONFIG_PATH"))
    return data["admins"]

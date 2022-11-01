# Телеграм бот для фильтра сообщений и бана пользователей

Pet-project

## Функции на данный момент

- Удаление слов, содержащих мат и кастомные слова.
- "Тихий" бан пользователей по id, username и fullname.

## *Admin only commands*

- Добавление кастомных слов для фильтра.
- Возможность "тихого" бана пользователя по id, username и fullname.

## Installation

Clone the project via https

```bash
git clone https://github.com/SerHappy/shh_bot.git
```

Or via SSH

```bash
git clone git@github.com:SerHappy/shh_bot.git
```

Go to the project directory

```bash
cd shh_bot
```

Create virtual environment

```bash
python3 -m venv env
```

Install requirements.txt

```bash
pip install -r requirements.txt
```

Rename env_example to .env and fill fields

Install requirements.txt

```bash
pip install -r requirements.txt
```

Run bot

```bash
python3 ./bot/__main__.py
```

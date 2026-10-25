"""
session_login.py - вход в Telegram по номеру телефона через Telethon.

Создаёт готовый файл сессии (<телефон>.session), которым потом можно
пользоваться в любом скрипте на Telethon. Никуда, кроме серверов
Telegram, ничего не отправляет.

Перед запуском получите свои api_id/api_hash на https://my.telegram.org
(раздел "API development tools") и впишите их ниже или передайте через
переменные окружения TG_API_ID / TG_API_HASH.

Использование:
    pip install -r requirements.txt
    python session_login.py +79991234567
"""
import asyncio
import os
import sys

from telethon import TelegramClient
from telethon.errors import (
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    SessionPasswordNeededError,
    PasswordHashInvalidError,
    FloodWaitError,
)

API_ID = int(os.environ.get("TG_API_ID", "0"))
API_HASH = os.environ.get("TG_API_HASH", "")


async def login(phone: str) -> None:
    if not API_ID or not API_HASH:
        print("Укажите TG_API_ID и TG_API_HASH (переменные окружения) - получить на my.telegram.org")
        return

    client = TelegramClient(phone, API_ID, API_HASH)
    await client.connect()

    if await client.is_user_authorized():
        print(f"Сессия {phone}.session уже авторизована, выход не нужен.")
        await client.disconnect()
        return

    try:
        sent = await client.send_code_request(phone)
    except FloodWaitError as e:
        print(f"Telegram просит подождать {e.seconds} секунд перед повторной попыткой.")
        await client.disconnect()
        return

    code = input("Код из Telegram: ").strip()
    try:
        await client.sign_in(phone=phone, code=code, phone_code_hash=sent.phone_code_hash)
    except SessionPasswordNeededError:
        password = input("Облачный пароль (2FA): ").strip()
        try:
            await client.sign_in(password=password)
        except PasswordHashInvalidError:
            print("Неверный пароль. Запустите скрипт заново.")
            await client.disconnect()
            return
    except PhoneCodeInvalidError:
        print("Неверный код. Запустите скрипт заново.")
        await client.disconnect()
        return
    except PhoneCodeExpiredError:
        print("Код устарел. Запустите скрипт заново.")
        await client.disconnect()
        return

    me = await client.get_me()
    print(f"Готово: вошли как {me.first_name} (id {me.id}). Файл сессии: {phone}.session")
    await client.disconnect()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python session_login.py +79991234567")
        sys.exit(1)
    asyncio.run(login(sys.argv[1]))

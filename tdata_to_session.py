"""
tdata_to_session.py - конвертер папки tdata (Telegram Desktop) в файл
сессии Telethon (.session).

Папка tdata лежит там, куда установлен Telegram Desktop, обычно:
  Windows: %APPDATA%\\Telegram Desktop\\tdata
  Linux:   ~/.local/share/TelegramDesktop/tdata

Скрипт не изменяет исходную папку tdata - только читает её и создаёт
новый файл <имя>.session рядом с собой. Основан на открытой библиотеке
opentele (https://github.com/thedemons/opentele).

Использование:
    pip install -r requirements.txt
    python tdata_to_session.py "C:/Users/you/AppData/Roaming/Telegram Desktop/tdata" my_account
"""
import asyncio
import sys

from opentele.td import TDesktop
from opentele.api import UseCurrentSession


async def convert(tdata_path: str, out_name: str) -> None:
    tdesk = TDesktop(tdata_path)
    if not tdesk.isLoaded():
        print(f"Не удалось прочитать tdata по пути: {tdata_path}")
        return

    client = await tdesk.ToTelethon(session=f"{out_name}.session", flag=UseCurrentSession)
    await client.connect()

    if not await client.is_user_authorized():
        print("Сессия не авторизована - возможно, аккаунт уже вышел из Telegram Desktop.")
        await client.disconnect()
        return

    me = await client.get_me()
    print(f"Готово: {me.first_name} (id {me.id}). Файл сессии: {out_name}.session")
    await client.disconnect()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Использование: python tdata_to_session.py "путь/к/tdata" имя_файла')
        sys.exit(1)
    asyncio.run(convert(sys.argv[1], sys.argv[2]))

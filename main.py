import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from config import BOT_TOKEN, ADMIN_ID
from core.db import init_db, save_search
from modules.username import search_username
from modules.email import search_email
from modules.phone import search_phone

# --- Логирование ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Инициализация бота ---
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ========== ПРОВЕРКА ДОСТУПА ==========
def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


# ========== КОМАНДЫ ==========

@dp.message(Command("start"))
async def cmd_start(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Доступ запрещён.")
        return

    await message.answer(
        "🔍 *OSINT-бот*\n\n"
        "Доступные команды:\n"
        "`/check <username>` — поиск по юзернейму\n"
        "`/email <email>` — поиск по email\n"
        "`/phone <номер> [регион]` — информация по номеру телефона\n"
        "`/help` — справка\n\n"
        "_Все данные хранятся локально и не публикуются._",
        parse_mode="Markdown"
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await cmd_start(message)


# ---------- /check ----------
@dp.message(Command("check"))
async def cmd_check(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Доступ запрещён.")
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "❌ Укажите юзернейм. Пример: `/check john_doe`",
            parse_mode="Markdown"
        )
        return

    username = args[1].strip().lstrip("@")
    await message.answer(f"🔎 Ищу `{username}`...", parse_mode="Markdown")

    result = await search_username(username)

    if "error" in result:
        await message.answer(f"❌ Ошибка: {result['error']}")
        return

    if result["count"] == 0:
        await message.answer(f"❌ Ничего не найдено для `{username}`.", parse_mode="Markdown")
        return

    text = f"✅ Найдено на *{result['count']}* сайтах:\n\n"
    for item in result["found"][:25]:
        text += f"• {item['site']}: {item['url']}\n"
    if result["count"] > 25:
        text += f"\n_...и ещё {result['count'] - 25}_"

    await message.answer(text, disable_web_page_preview=True, parse_mode="Markdown")
    save_search(message.from_user.id, "username", username, f"{result['count']} sites")


# ---------- /email ----------
@dp.message(Command("email"))
async def cmd_email(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Доступ запрещён.")
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "❌ Укажите email. Пример: `/email test@example.com`",
            parse_mode="Markdown"
        )
        return

    email = args[1].strip()
    await message.answer(f"🔎 Ищу `{email}`...", parse_mode="Markdown")

    result = await search_email(email)

    if "error" in result:
        await message.answer(f"❌ Ошибка: {result['error']}")
        return

    if not result["found"]:
        await message.answer(f"❌ Регистраций не найдено для `{email}`.", parse_mode="Markdown")
        return

    text = f"✅ Найдено регистраций: *{result['count']}*\n\n"
    for item in result["found"][:25]:
        text += f"• {item}\n"

    await message.answer(text, parse_mode="Markdown")
    save_search(message.from_user.id, "email", email, f"{result['count']} sites")


# ---------- /phone ----------
@dp.message(Command("phone"))
async def cmd_phone(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Доступ запрещён.")
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "❌ Укажите номер. Пример: `/phone +79123456789`\n"
            "Регион по умолчанию — RU. Можно указать вручную: `/phone 89123456789 KZ`",
            parse_mode="Markdown"
        )
        return

    parts = args[1].strip().split()
    number = parts[0]
    region = parts[1].upper() if len(parts) > 1 else "RU"

    await message.answer(f"📞 Ищу информацию о `{number}`...", parse_mode="Markdown")

    result = await search_phone(number, region)

    if "error" in result:
        await message.answer(f"❌ Ошибка: {result['error']}")
        return

    text = (
        f"📞 *{result['international']}*\n\n"
        f"🌍 Страна: {result.get('location') or 'неизвестно'}\n"
        f"🔢 Регион: {result['region_code']} (код +{result['country_code']})\n"
        f"🏢 Оператор: {result.get('carrier') or 'неизвестно'}\n"
        f"📱 Тип линии: {result['line_type']}\n"
        f"🕐 Часовой пояс: {', '.join(result.get('timezone', []))}\n"
    )

    if result.get("numverify_carrier"):
        text += f"\n_Numverify_: {result['numverify_carrier']}, {result.get('numverify_location', '')}"

    await message.answer(text, parse_mode="Markdown")

    links = result.get("manual_links", {})
    if links:
        links_text = "🔗 *Проверить вручную:*\n" + "\n".join(
            f"• [{name}]({url})" for name, url in links.items()
        )
        await message.answer(links_text, parse_mode="Markdown", disable_web_page_preview=True)

    save_search(
        message.from_user.id,
        "phone",
        number,
        f"{result.get('carrier', '?')}, {result.get('location', '?')}"
    )


# ========== ЗАПУСК ==========
async def main():
    init_db()
    logger.info("Бот запущен...")
    await dp.start_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())

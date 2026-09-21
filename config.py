import os
from dotenv import load_dotenv

# Загружаем .env только для локального запуска.
# На Railway переменные приходят напрямую из окружения.
load_dotenv()

# --- Обязательные переменные ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# --- Опциональные переменные ---
NUMVERIFY_API_KEY = os.getenv("NUMVERIFY_API_KEY", "")
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID", "")

# --- Проверка обязательных переменных ---
if not BOT_TOKEN:
    raise ValueError(
        "❌ BOT_TOKEN не задан. "
        "На Railway добавьте его в разделе Variables. "
        "Локально — создайте файл .env с BOT_TOKEN=..."
    )

if ADMIN_ID == 0:
    raise ValueError(
        "❌ ADMIN_ID не задан. "
        "Узнайте свой ID у @userinfobot и добавьте в переменные окружения.")

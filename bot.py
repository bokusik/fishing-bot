import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, MenuButtonWebApp, WebAppInfo
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загрузка конфигурации
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY")

# База данных водоёмов
WATER_POINTS = {
    "Шебеньгское озеро": {
        "coords": [60.600, 43.450],
        "fish_rating": 4,
        "depth": "4-8 м",
        "fish_types": ["щука", "окунь", "плотва"],
        "photo": "https://example.com/shebeng.jpg"
    },
    "Озеро Ромашевское": {
        "coords": [60.489, 43.352],
        "fish_rating": 3,
        "depth": "5-10 м",
        "fish_types": ["лещ", "окунь", "язь"],
        "photo": "https://example.com/romashev.jpg"
    }
}

WIND_LEVELS = {
    (0, 0.3): ("🌀 Безветрие", "🎣 Идеально для рыбалки"),
    (0.3, 1.5): ("🌬 Легкий ветерок", "🎣 Отличные условия"),
    (1.5, 3.3): ("🍃 Умеренный ветер", "🎣 Хороший клёв"),
    (3.3, 5.4): ("🌪 Сильный ветер", "🎣 Рыба клюет осторожно"),
    (5.4, float('inf')): ("⚠️ Штормовой ветер", "❌ Неблагоприятно для ловли")
}

class FishingBot:
    @staticmethod
    def get_pressure_status(pressure_mb):
        if pressure_mb < 1000:
            return "низкое", "🟢 Благоприятное"
        elif 1000 <= pressure_mb <= 1010:
            return "среднее", "🟡 Нормальное"
        return "высокое", "🔴 Неблагоприятное"

    @staticmethod
    def get_wind_description(wind_speed):
        for (min_speed, max_speed), (description, fishing_tip) in WIND_LEVELS.items():
            if min_speed <= wind_speed < max_speed:
                return description, fishing_tip
        return "🌫 Неизвестно", ""

    @staticmethod
    async def send_menu(update: Update):
        keyboard = [
            [InlineKeyboardButton(name, callback_data=name)]
            for name in WATER_POINTS.keys()
        ]
        await update.message.reply_text(
            "🎣 <b>Рыболовный гид</b>\nВыберите водоём:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )

    @staticmethod
    async def get_weather_report(point_name: str, point_data: dict):
        try:
            lat, lon = point_data["coords"]
            url = f"http://api.weatherapi.com/v1/current.json?key={WEATHERAPI_KEY}&q={lat},{lon}&lang=ru"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            weather = response.json()["current"]
            
            wind_speed = weather["wind_kph"] * 0.277778
            pressure_status, pressure_emoji = FishingBot.get_pressure_status(weather["pressure_mb"])
            wind_desc, wind_tip = FishingBot.get_wind_description(wind_speed)
            
            return (
                f"🌊 <b>{point_name}</b>\n"
                f"📍 Глубина: {point_data['depth']}\n"
                f"🐟 Рыба: {', '.join(point_data['fish_types'])}\n\n"
                f"🎣 <b>Прогноз клёва:</b>\n"
                f"⭐ Рейтинг: {'⭐' * point_data['fish_rating']}\n"
                f"⏲ Давление: {weather['pressure_mb']} гПа ({pressure_status}) {pressure_emoji}\n"
                f"{wind_desc} - {wind_tip}\n\n"
                f"🌡 Температура: {weather['temp_c']}°C\n"
                f"💨 Ветер: {wind_speed:.1f} м/с ({weather['wind_dir']})\n"
                f"💧 Влажность: {weather['humidity']}%\n\n"
                f"🕒 Обновлено: {weather['last_updated']}"
            )
        except Exception as e:
            logger.error(f"Ошибка при получении погоды: {e}")
            return None

async def setup_menu(app: Application):
    await app.bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="Открыть карту",
            web_app=WebAppInfo(url="https://fishing-bot.vercel.app")
        )
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Выберите действие:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🌐 Открыть карту", web_app=WebAppInfo(url="https://fishing-bot.vercel.app"))],
            [InlineKeyboardButton("🎣 Список водоёмов", callback_data="menu")]
        ])
    )

# [Остальные обработчики handle_water_point, back_to_menu и т.д. остаются без изменений]

def main():
    app = Application.builder().token(TOKEN).post_init(setup_menu).build()
    
    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop_bot))
    app.add_handler(CallbackQueryHandler(handle_water_point, pattern="^(?!back|menu).*$"))
    app.add_handler(CallbackQueryHandler(back_to_menu, pattern="^back$"))
    app.add_handler(CallbackQueryHandler(start, pattern="^menu$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_error_handler(error_handler)
    
    app.run_polling()

if __name__ == "__main__":
    main()
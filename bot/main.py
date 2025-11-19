import os
from aiogram import Bot, Dispatcher
from aiogram import types
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # ID чата, куда присылать данные

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


# --- ROUTE эндпоинт, который принимает форму ---
async def form_handler(request: web.Request):
    data = await request.json()

    email = data.get("email")
    company = data.get("company")
    phone = data.get("phone")
    description = data.get("description")

    text = (
        "<b>Новая заявка</b>\n\n"
        f"📧 Email: {email}\n"
        f"🏢 Компания: {company}\n"
        f"📱 Телефон: {phone}\n"
        f"📝 Описание: {description}"
    )

    await bot.send_message(CHAT_ID, text)
    return web.json_response({"status": "ok"})


async def on_startup(app: web.Application):
    await bot.send_message(
        os.getenv("CHAT_ID"),
        "🤖 Бот запущен и находится в сети!"
    )
    print("Startup message sent")


@dp.message()
async def echo_handler(message: types.Message):
    await message.answer(f"Эхо: {message.text}")


def main():
    app = web.Application()

    # Регистрируем endpoint формы
    app.router.add_post("/form-handler", form_handler)

    # Регистрируем startup callback
    app.on_startup.append(on_startup)

    # Подключаем aiogram webhooks (если хотите — можно оставить только handler)
    SimpleRequestHandler(dp, bot).register(app, path="/webhook")
    setup_application(app, dp, bot=bot)

    web.run_app(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()

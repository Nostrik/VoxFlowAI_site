import os
from aiogram import Bot, Dispatcher
from aiogram import types
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

async def form_handler(request: web.Request):
    try:
        print("=== ПОЛУЧЕН ЗАПРОС НА /form-handler ===")
        print("Заголовки:", dict(request.headers))
        
        data = await request.json()
        print("Данные из формы:", data)

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
        print("Сообщение отправлено в Telegram")
        
        return web.json_response({"status": "ok"})
    
    except Exception as e:
        print(f"ОШИБКА в form_handler: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)

async def options_handler(request):
    """Обработчик CORS preflight запросов"""
    return web.Response(
        status=200,
        headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '86400',
        }
    )

async def cors_middleware(app, handler):
    """Middleware для добавления CORS headers ко всем ответам"""
    async def middleware(request):
        # Обрабатываем OPTIONS запросы
        if request.method == 'OPTIONS':
            return await options_handler(request)
        
        # Обрабатываем обычные запросы
        response = await handler(request)
        
        # Добавляем CORS headers
        response.headers.update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        })
        return response
    return middleware

async def on_startup(app: web.Application):
    try:
        await bot.send_message(CHAT_ID, "🤖 Бот запущен и находится в сети!")
        print("Startup message sent successfully!")
    except Exception as e:
        print(f"Failed to send startup message: {e}")

@dp.message()
async def echo_handler(message: types.Message):
    await message.answer(f"Эхо: {message.text}")

def main():
    # Создаем приложение с CORS middleware
    app = web.Application(middlewares=[cors_middleware])
    
    # Добавляем маршруты
    app.router.add_post("/form-handler", form_handler)
    
    # Регистрируем обработчики aiogram
    SimpleRequestHandler(dp, bot).register(app, path="/webhook")
    setup_application(app, dp, bot=bot)

    app.on_startup.append(on_startup)

    print("🚀 Сервер запущен на http://localhost:8080")
    print("📝 Форма будет отправлять данные на http://localhost:8080/form-handler")
    
    web.run_app(app, host="0.0.0.0", port=8080)

if __name__ == "__main__":
    main()
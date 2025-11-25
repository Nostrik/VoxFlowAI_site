import os
import pytz
import configparser
import json
from aiogram import Bot, Dispatcher
from aiogram import types
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from datetime import datetime, timedelta

from json_storage import (
    get_next_request_number,
    save_request_to_json,
    get_request_statistics,
    search_requests,
    get_request_by_id,
    get_recent_requests,
    initialize_storage
)

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

COUNTER_FILE = "request_counter.ini"

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


async def form_handler(request: web.Request):
    try:
        # Получаем следующий номер заявки
        request_number = get_next_request_number()
        print(f"Получена заявка №{request_number} на /form-handler")

        # Парсим JSON данные
        data = await request.json()
        print("Данные:", data)

        print("=== ПОЛУЧЕН ЗАПРОС НА /form-handler ===")
        print("Заголовки:", dict(request.headers))
        
        data = await request.json()
        print("Данные из формы:", data)

        # Извлекаем основные поля
        email = data.get("email", "").strip()
        company = data.get("company", "").strip()
        phone = data.get("phone", "").strip()
        description = data.get("description", "").strip()

        # Подготавливаем временные метки
        moscow_time = datetime.now() + timedelta(hours=3)
        date_time_display = moscow_time.strftime("%d.%m.%Y %H:%M:%S")
        timestamp = moscow_time.isoformat()

        # Собираем дополнительные метаданные
        headers = dict(request.headers)
        
        # Формируем полную структуру данных
        request_data = {
            "request_id": request_number,
            "timestamp": datetime.now().isoformat(),
            "datetime_display": date_time_display,
            "email": email,
            "company": company,
            "phone": phone,
            "description": description,
            "ip_address": request.remote,
        }

        # Сохраняем в JSON используя импортированную функцию
        saved_request = save_request_to_json(request_data)
        print(f"✅ Заявка №{request_number} сохранена в JSON")
        
        if not saved_request:
            return web.json_response({
                "status": "error", 
                "message": "Ошибка сохранения данных"
            }, status=500)

        text = (
            f"<b>🆕 Новая заявка №{request_number} ({date_time_display})</b>\n\n"
            f"📧 Email: {email}\n"
            f"🏢 Компания: {company}\n"
            f"📱 Телефон: {phone}\n"
            f"📝 Описание: {description}"
        )

        await bot.send_message(CHAT_ID, text)
        print("Сообщение отправлено в Telegram")
        
        return web.json_response({
            "status": "ok", 
            "request_id": request_number,
            "message": "Заявка успешно отправлена и сохранена",
            "timestamp": timestamp
        })
    
    except json.JSONDecodeError:
        return web.json_response({
            "status": "error", 
            "message": "Ошибка формата JSON"
        }, status=400)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return web.json_response({
            "status": "error", 
            "message": "Внутренняя ошибка сервера"
        }, status=500)
    

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


# API endpoints использующие импортированные функции
async def stats_handler(request: web.Request):
    """API endpoint для получения статистики"""
    stats = get_request_statistics()
    return web.json_response(stats)


async def search_handler(request: web.Request):
    """API endpoint для поиска заявок"""
    query = request.query.get('q', '')
    field = request.query.get('field', 'all')
    
    if not query:
        return web.json_response({"error": "Не указан поисковый запрос"}, status=400)
    
    results = search_requests(query, field)
    return web.json_response({
        "query": query,
        "field": field,
        "results": results,
        "count": len(results)
    })


async def request_by_id_handler(request: web.Request):
    """API endpoint для получения заявки по ID"""
    request_id = request.match_info.get('id')
    
    if not request_id or not request_id.isdigit():
        return web.json_response({"error": "Неверный ID заявки"}, status=400)
    
    request_data = get_request_by_id(int(request_id))
    
    if not request_data:
        return web.json_response({"error": "Заявка не найдена"}, status=404)
    
    return web.json_response(request_data)


async def recent_requests_handler(request: web.Request):
    """API endpoint для получения последних заявок"""
    limit = request.query.get('limit', '10')
    
    try:
        limit = int(limit)
        if limit > 100:  # Ограничиваем максимальное количество
            limit = 100
    except ValueError:
        limit = 10
    
    recent = get_recent_requests(limit)
    return web.json_response({
        "limit": limit,
        "requests": recent
    })


async def on_startup(app: web.Application):
    """Действия при запуске сервера"""
    try:
        await bot.send_message(CHAT_ID, "🤖 Бот запущен и находится в сети!")
        print("Startup message sent successfully!")
    except Exception as e:
        print(f"Failed to send startup message: {e}")


def main():
     # Инициализируем систему хранения
    initialize_storage()

    # Создаем приложение с CORS middleware
    app = web.Application(middlewares=[cors_middleware])
    
    # Добавляем маршруты
    app.router.add_post("/form-handler", form_handler)
    app.router.add_get("/stats", stats_handler)
    app.router.add_get("/search", search_handler)
    app.router.add_get("/request/{id}", request_by_id_handler)
    app.router.add_get("/recent", recent_requests_handler)
    
    # Регистрируем обработчики aiogram
    SimpleRequestHandler(dp, bot).register(app, path="/webhook")
    setup_application(app, dp, bot=bot)

    app.on_startup.append(on_startup)

    print("🚀 Сервер запущен на http://localhost:8080")
    print("📝 Форма будет отправлять данные на http://88.210.53.86:8080/form-handler")
    
    web.run_app(app, host="0.0.0.0", port=8080)

if __name__ == "__main__":
    main()
    
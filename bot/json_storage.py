# json_storage.py
"""
Модуль для работы с хранением заявок в JSON файлах
"""

import json
import os
import configparser
from datetime import datetime, timedelta
import shutil
from typing import List, Dict, Any, Optional

# Конфигурационные константы
DATA_DIR = "bot_data"
COUNTER_FILE = os.path.join(DATA_DIR, "request_counter.ini")
REQUESTS_DIR = os.path.join(DATA_DIR, "requests_data")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")

def ensure_directories():
    """Создаем необходимые директории если их нет"""
    for directory in [REQUESTS_DIR, BACKUP_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Создана директория: {directory}")

def get_next_request_number() -> int:
    """
    Получаем следующий номер заявки из INI-файла
    
    Returns:
        int - следующий номер заявки
    """
    config = configparser.ConfigParser()
    
    if os.path.exists(COUNTER_FILE):
        try:
            config.read(COUNTER_FILE)
            current = int(config['COUNTER']['current'])
        except (KeyError, ValueError):
            current = 0
    else:
        current = 0
    
    next_number = current + 1
    config['COUNTER'] = {'current': str(next_number)}
    
    try:
        with open(COUNTER_FILE, 'w') as configfile:
            config.write(configfile)
    except Exception as e:
        print(f"⚠️ Ошибка сохранения счетчика: {e}")
    
    return next_number

def get_current_requests_file() -> str:
    """
    Генерируем имя файла для текущего месяца
    
    Returns:
        str - путь к файлу текущего месяца
    """
    current_month = datetime.now().strftime("%Y-%m")
    filename = f"requests_{current_month}.json"
    return os.path.join(REQUESTS_DIR, filename)

def get_all_requests_files() -> List[str]:
    """
    Получаем список всех JSON файлов с заявками
    
    Returns:
        List[str] - список путей к файлам
    """
    if not os.path.exists(REQUESTS_DIR):
        return []
    
    files = []
    for filename in os.listdir(REQUESTS_DIR):
        if filename.startswith("requests_") and filename.endswith(".json"):
            files.append(os.path.join(REQUESTS_DIR, filename))
    
    return sorted(files)

def create_backup():
    """Создаем бэкап текущего месяца"""
    try:
        current_file = get_current_requests_file()
        if os.path.exists(current_file):
            backup_name = f"backup_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
            backup_path = os.path.join(BACKUP_DIR, backup_name)
            
            shutil.copy2(current_file, backup_path)
            print(f"💾 Создан бэкап: {backup_path}")
    except Exception as e:
        print(f"⚠️ Ошибка создания бэкапа: {e}")

def save_request_to_json(request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Сохраняем заявку в JSON файл
    
    Args:
        request_data: Данные заявки
        
    Returns:
        Dict или None в случае ошибки
    """
    ensure_directories()
    requests_file = get_current_requests_file()
    
    # Полная структура записи
    request_record = {
        "request_id": request_data["request_id"],
        "timestamp": request_data["timestamp"],
        "datetime_display": request_data["datetime_display"],
        "email": request_data["email"],
        "company": request_data["company"],
        "phone": request_data["phone"],
        "description": request_data["description"],
        "ip_address": request_data.get("ip_address", "unknown"),
        "user_agent": request_data.get("user_agent", "unknown"),
        "headers": request_data.get("headers", {}),
        "method": request_data.get("method", "POST"),
        "url": request_data.get("url", "/form-handler")
    }
    
    # Читаем существующие данные
    existing_requests = []
    if os.path.exists(requests_file):
        try:
            with open(requests_file, 'r', encoding='utf-8') as f:
                existing_requests = json.load(f)
        except (json.JSONDecodeError, Exception):
            existing_requests = []
    
    # Добавляем новую заявку
    existing_requests.append(request_record)
    
    # Сохраняем обратно в файл
    try:
        with open(requests_file, 'w', encoding='utf-8') as f:
            json.dump(existing_requests, f, 
                     ensure_ascii=False,
                     indent=2,
                     default=str)
        
        print(f"✅ Заявка №{request_data['request_id']} сохранена в JSON")
        
        # Создаем бэкап каждые 10 заявок
        if request_data["request_id"] % 10 == 0:
            create_backup()
            
        return request_record
        
    except Exception as e:
        print(f"❌ Ошибка сохранения заявки: {e}")
        
        # Пытаемся сохранить в резервный файл
        try:
            backup_file = os.path.join(REQUESTS_DIR, f"emergency_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json")
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump([request_record], f, ensure_ascii=False, indent=2)
            print(f"⚠️ Заявка сохранена в аварийный файл: {backup_file}")
        except:
            print("❌ Критическая ошибка: не удалось сохранить заявку")
        
        return None

def get_request_statistics() -> Dict[str, Any]:
    """
    Получаем подробную статистику по заявкам
    
    Returns:
        Dict со статистикой
    """
    all_files = get_all_requests_files()
    total_requests = 0
    monthly_stats = {}
    
    for filepath in all_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                requests = json.load(f)
            
            filename = os.path.basename(filepath)
            month = filename.replace('requests_', '').replace('.json', '')
            monthly_stats[month] = len(requests)
            total_requests += len(requests)
            
        except Exception:
            continue
    
    return {
        "total_requests": total_requests,
        "monthly_stats": monthly_stats,
        "current_month": datetime.now().strftime("%Y-%m"),
        "files_count": len(all_files),
        "storage_dir": REQUESTS_DIR
    }

def search_requests(search_term: str, field: str = "all") -> List[Dict[str, Any]]:
    """
    Поиск заявок по различным полям
    
    Args:
        search_term: поисковый запрос
        field: поле для поиска (all, email, company, phone, description)
        
    Returns:
        List найденных заявок
    """
    results = []
    all_files = get_all_requests_files()
    
    if not search_term:
        return results
    
    search_term = search_term.lower()
    
    for filepath in all_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                requests = json.load(f)
            
            for request in requests:
                match = False
                
                if field == "all" or field == "email":
                    if search_term in request.get('email', '').lower():
                        match = True
                
                if not match and (field == "all" or field == "company"):
                    if search_term in request.get('company', '').lower():
                        match = True
                
                if not match and (field == "all" or field == "phone"):
                    if search_term in request.get('phone', '').lower():
                        match = True
                
                if not match and (field == "all" or field == "description"):
                    if search_term in request.get('description', '').lower():
                        match = True
                
                if match:
                    results.append(request)
                    
        except Exception:
            continue
    
    return sorted(results, key=lambda x: x.get('timestamp', ''), reverse=True)

def get_request_by_id(request_id: int) -> Optional[Dict[str, Any]]:
    """
    Находим заявку по ID
    
    Args:
        request_id: ID заявки
        
    Returns:
        Dict с данными заявки или None
    """
    all_files = get_all_requests_files()
    
    for filepath in all_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                requests = json.load(f)
            
            for request in requests:
                if request.get('request_id') == request_id:
                    return request
                    
        except Exception:
            continue
    
    return None

def get_recent_requests(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Получаем последние заявки
    
    Args:
        limit: количество заявок
        
    Returns:
        List последних заявок
    """
    all_requests = []
    all_files = get_all_requests_files()
    
    for filepath in all_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                requests = json.load(f)
            all_requests.extend(requests)
        except Exception:
            continue
    
    # Сортируем по timestamp и возвращаем limit последних
    sorted_requests = sorted(all_requests, 
                           key=lambda x: x.get('timestamp', ''), 
                           reverse=True)
    
    return sorted_requests[:limit]

def initialize_storage():
    """Инициализация системы хранения"""
    ensure_directories()
    print("✅ JSON storage system initialized")
    print(f"📁 Data directory: {REQUESTS_DIR}")
    print(f"📁 Backup directory: {BACKUP_DIR}")
    
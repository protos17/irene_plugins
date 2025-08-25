# Плагин для получения новостей через NewsAPI
# author: protos17
# Необходимо установить pip install newsapi-python

import os
from datetime import datetime, timedelta
from vacore import VACore

modname = os.path.basename(__file__)[:-3] # calculating modname

# функция на старте
def start(core: VACore):
    manifest = {
        "name": "Новости NewsAPI",
        "version": "1.1",
        "require_online": True,
        "description": "Получение новостей через NewsAPI. Главные новости России, мира, новости из RBC, Lenta.ru",

        "options_label": {
            "api_key": "API ключ NewsAPI (получить на newsapi.org)",
            "page_size": "Количество новостей для получения (1-10)",
            "language": "Язык новостей (ru, en)"
        },

        "default_options": {
            "api_key": "",
            "page_size": "5",
            "language": "ru"
        },

        "commands": {
            "новости|последние новости|что нового": get_general_news,
            "главные новости|новости россии|российские новости": get_russia_news,
            "новости мира|мировые новости|новости зарубежья": get_world_news,
            "новости рбк|рбк|новости из рбк": get_rbc_news,
            "новости лента|лента|новости из ленты": get_lenta_news,
            "технические новости|новости технологий": get_tech_news,
            "спортивные новости|новости спорта": get_sports_news,
        }
    }
    return manifest

def start_with_options(core: VACore, manifest: dict):
    pass

def get_newsapi_client(api_key: str):
    """Создает и возвращает клиент NewsAPI"""
    try:
        from newsapi import NewsApiClient
        return NewsApiClient(api_key=api_key)
    except ImportError:
        raise ImportError("Библиотека newsapi-python не установлена. Установите: pip install newsapi-python")

def get_news(core: VACore, news_type: str, sources: str = None, category: str = None, country: str = None):
    """Базовая функция получения новостей"""
    options = core.plugin_options(modname)
    api_key = options["api_key"]
    
    if not api_key:
        core.play_voice_assistant_speech("Нужен API ключ для NewsAPI. Получите его на newsapi.org и укажите в настройках плагина.")
        return
    
    try:
        newsapi = get_newsapi_client(api_key)
        
        page_size = int(options.get("page_size", 5))
        page_size = min(max(page_size, 1), 10)
        
        # Получаем новости в зависимости от типа запроса
        if sources:
            # Новости из конкретных источников
            all_articles = newsapi.get_top_headlines(
                sources=sources,
                language=options.get("language", "ru"),
                page_size=page_size
            )
        elif category:
            # Новости по категории
            all_articles = newsapi.get_top_headlines(
                category=category,
                language=options.get("language", "ru"),
                page_size=page_size
            )
        elif country:
            # Новости по стране
            all_articles = newsapi.get_top_headlines(
                country=country,
                language=options.get("language", "ru"),
                page_size=page_size
            )
        else:
            # Общие новости
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            all_articles = newsapi.get_everything(
                language=options.get("language", "ru"),
                sort_by='publishedAt',
                page_size=page_size,
                from_param=yesterday
            )
        
        articles = all_articles.get('articles', [])
        
        if not articles:
            core.play_voice_assistant_speech(f"{news_type} не найдены. Попробуйте позже.")
            return
        
        # Озвучиваем новости
        core.play_voice_assistant_speech(f"Вот {news_type.lower()}:")
        
        for i, article in enumerate(articles[:3]):  # Ограничиваем 3 новостями
            title = article.get('title', '')
            source = article.get('source', {}).get('name', '')
            
            if title:
                # Очищаем заголовок для озвучивания
                clean_title = clean_news_title(title, source)
                
                news_text = f"Новость {i+1}"
                if source and len(articles) > 1:
                    news_text += f" из {source}"
                news_text += f": {clean_title}"
                
                core.play_voice_assistant_speech(news_text)
                
                # Небольшая пауза между новостями
                import time
                time.sleep(1)
        
        core.play_voice_assistant_speech("Вот и все новости.")
        
    except ImportError:
        core.play_voice_assistant_speech("Для работы новостей нужно установить библиотеку newsapi-python. Установите: pip install newsapi-python")
    
    except Exception as e:
        print(f"Ошибка получения новостей: {e}")
        core.play_voice_assistant_speech("Не удалось получить новости. Проверьте подключение к интернету и настройки API.")

def clean_news_title(title: str, source: str) -> str:
    """Очищает заголовок новости для лучшего озвучивания"""
    # Убираем источник из заголовка если он есть
    if source and source in title:
        title = title.replace(source, '').strip()
    
    # Убираем разделители
    separators = [' - ', ' | ', ' :: ', ' – ']
    for sep in separators:
        if sep in title:
            parts = title.split(sep)
            # Берем первую часть (обычно это основной заголовок)
            title = parts[0].strip()
            break
    
    # Убираем лишние пробелы
    title = ' '.join(title.split())
    
    return title

def get_general_news(core: VACore, phrase: str):
    """Общие последние новости"""
    get_news(core, "Последние новости")

def get_russia_news(core: VACore, phrase: str):
    """Главные новости России"""
    get_news(core, "Главные новости России", country='ru')

def get_world_news(core: VACore, phrase: str):
    """Новости мира"""
    # Используем everything для международных новостей
    get_news(core, "Новости мира")

def get_rbc_news(core: VACore, phrase: str):
    """Новости из RBC"""
    get_news(core, "Новости из РБК", sources='rbc')

def get_lenta_news(core: VACore, phrase: str):
    """Новости из Lenta.ru"""
    get_news(core, "Новости из Лента.ru", sources='lenta')

def get_tech_news(core: VACore, phrase: str):
    """Технические новости"""
    get_news(core, "Технические новости", category='technology')

def get_sports_news(core: VACore, phrase: str):
    """Спортивные новости"""
    get_news(core, "Спортивные новости", category='sports')
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
        "version": "1.0",
        "require_online": True,
        "description": "Получение последних новостей России из источника Kommersant.ru через NewsAPI",

        "options_label": {
            "api_key": "API ключ NewsAPI (получить на newsapi.org)",
            "page_size": "Количество новостей для получения (1-10)",
            "language": "Язык новостей"
        },

        "default_options": {
            "api_key": "",
            "page_size": "5",
            "language": "ru"
        },

        "commands": {
            "новости|последние новости|что нового|новости коммерсанта": get_news,
            "главные новости|свежие новости": get_top_news,
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

def get_news(core: VACore, phrase: str):
    """Получение последних новостей"""
    options = core.plugin_options(modname)
    api_key = options["api_key"]
    
    if not api_key:
        core.play_voice_assistant_speech("Нужен API ключ для NewsAPI. Получите его на newsapi.org и укажите в настройках плагина.")
        return
    
    try:
        # Импортируем библиотеку
        newsapi = get_newsapi_client(api_key)
        
        # Получаем дату вчерашнего дня для свежих новостей
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Получаем новости из Kommersant.ru
        try:
            page_size = int(options.get("page_size", 5))
            page_size = min(max(page_size, 1), 10)  # Ограничиваем от 1 до 10
            
            all_articles = newsapi.get_everything(
                domains='kommersant.ru',
                from_param=yesterday,
                language=options.get("language", "ru"),
                sort_by='publishedAt',
                page_size=page_size
            )
            
            articles = all_articles.get('articles', [])
            
        except Exception as e:
            # Если не удалось получить конкретно Kommersant, пробуем общие новости России
            print(f"Ошибка получения Kommersant: {e}")
            all_articles = newsapi.get_top_headlines(
                country='ru',
                language=options.get("language", "ru"),
                page_size=page_size
            )
            articles = all_articles.get('articles', [])
        
        if not articles:
            core.play_voice_assistant_speech("Новости не найдены. Попробуйте позже.")
            return
        
        # Озвучиваем новости
        core.play_voice_assistant_speech("Вот последние новости:")
        
        for i, article in enumerate(articles[:3]):  # Ограничиваем 3 новостями
            title = article.get('title', '')
            if title:
                # Убираем источник в конце заголовка если есть
                if ' - ' in title:
                    title = title.split(' - ')[0]
                
                core.play_voice_assistant_speech(f"Новость {i+1}: {title}")
                
                # Небольшая пауза между новостями
                import time
                time.sleep(1)
        
        core.play_voice_assistant_speech("Вот и все свежие новости.")
        
    except ImportError:
        core.play_voice_assistant_speech("Для работы новостей нужно установить библиотеку newsapi-python. Установите: pip install newsapi-python")
    
    except Exception as e:
        print(f"Ошибка получения новостей: {e}")
        core.play_voice_assistant_speech("Не удалось получить новости. Проверьте подключение к интернету и настройки API.")

def get_top_news(core: VACore, phrase: str):
    """Получение главных новостей России"""
    options = core.plugin_options(modname)
    api_key = options["api_key"]
    
    if not api_key:
        core.play_voice_assistant_speech("Нужен API ключ для NewsAPI. Получите его на newsapi.org и укажите в настройках плагина.")
        return
    
    try:
        newsapi = get_newsapi_client(api_key)
        
        page_size = int(options.get("page_size", 5))
        page_size = min(max(page_size, 1), 10)
        
        # Получаем топовые новости России
        top_headlines = newsapi.get_top_headlines(
            country='ru',
            language=options.get("language", "ru"),
            page_size=page_size
        )
        
        articles = top_headlines.get('articles', [])
        
        if not articles:
            core.play_voice_assistant_speech("Главные новости не найдены. Попробуйте позже.")
            return
        
        # Озвучиваем новости
        core.play_voice_assistant_speech("Вот главные новости России:")
        
        for i, article in enumerate(articles[:3]):  # Ограничиваем 3 новостями
            title = article.get('title', '')
            source = article.get('source', {}).get('name', '')
            
            if title:
                # Упрощаем заголовок для озвучивания
                if ' - ' in title:
                    title = title.split(' - ')[0]
                
                news_text = f"Новость {i+1}"
                if source:
                    news_text += f" из {source}"
                news_text += f": {title}"
                
                core.play_voice_assistant_speech(news_text)
                
                import time
                time.sleep(1)
        
        core.play_voice_assistant_speech("Вот и все главные новости.")
        
    except ImportError:
        core.play_voice_assistant_speech("Для работы новостей нужно установить библиотеку newsapi-python. Установите: pip install newsapi-python")
    
    except Exception as e:
        print(f"Ошибка получения новостей: {e}")
        core.play_voice_assistant_speech("Не удалось получить главные новости. Проверьте подключение к интернету.")
import requests
from bs4 import BeautifulSoup

def fetch_article_text(url):
    """Загружает и извлекает текст статьи с указанного URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Вызовет исключение для HTTP ошибок (4xx, 5xx)

        soup = BeautifulSoup(response.text, 'html.parser')

        # Более надежный поиск контента:
        article_body = None
        for tag in ['article', 'div']:
            for class_name in ['content', 'post-body', 'article-body', 'main-content', 'entry-content']:  # Добавили больше классов
                article_body = soup.find(tag, class_=class_name)
                if article_body:
                    break
            if article_body:
                break


        if article_body:
             # Убираем скрипты и стили:
            for script_or_style in article_body(['script', 'style']):
                script_or_style.decompose()

            paragraphs = article_body.find_all('p')
            # Фильтруем пустые абзацы и короткие строки (часто это не контент):
            filtered_paragraphs = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20]
            return '\n'.join(filtered_paragraphs)

        return "Ошибка: Не удалось найти основное содержимое статьи." # Более понятная ошибка

    except requests.exceptions.RequestException as e:
        return f"Ошибка сети: {e}"  # Обработка ошибок соединения
    except Exception as e:
        return f"Ошибка при извлечении статьи: {e}"
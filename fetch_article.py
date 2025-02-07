import requests
from bs4 import BeautifulSoup

def fetch_article_text(url):
    """Загружает и извлекает текст статьи с указанного URL."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        article = soup.find('article') or soup.find('div', class_='content') or soup.find('div', class_='post-body')
        
        if article:
            paragraphs = article.find_all('p')
            return '\n'.join(p.get_text() for p in paragraphs)
        
        return "Не удалось извлечь текст статьи. Попробуйте другой URL."
    except Exception as e:
        return f"Ошибка загрузки статьи: {e}"

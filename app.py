import openai
from flask import Flask, render_template, request, flash
from dotenv import load_dotenv
import os
import logging  # Добавлено
import spacy  # Добавлено для извлечения ключевых слов

# Загрузка переменных окружения
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Настройка логирования
logging.basicConfig(level=logging.ERROR, filename="app_errors.log", format='%(asctime)s - %(levelname)s - %(message)s')

# Загружаем API-ключ OpenAI при старте приложения
openai.api_key = os.getenv('OPENAI_API_KEY')
if not openai.api_key:
    raise ValueError("API-ключ OpenAI не установлен! Установите переменную окружения OPENAI_API_KEY.")

# Загрузка модели spaCy (!!! Установи и скачай модель: pip install spacy; python -m spacy download ru_core_news_sm)
try:
    nlp = spacy.load("ru_core_news_sm")  # Или другую модель, если нужен другой язык
except OSError:
    logging.error("Не удалось загрузить модель spaCy 'ru_core_news_sm'. Убедитесь, что она установлена.")
    raise  #  Перезапускаем исключение, чтобы остановить приложение


PLATFORM_PROMPTS = {
    "twitter": "Ты – эксперт по контенту для Twitter (X). Напиши цепляющий твит на языке {output_language} на основе следующей новости: '{НОВОСТЬ}'. Длина: до 200 символов. Минимум 'воды', только суть! Можно добавить интригу или вопрос. В конце добавь 2-3 хештега.",
    "instagram": "Ты – профессиональный SMM-копирайтер. Напиши увлекательный Instagram-пост на языке {output_language} по новости: '{НОВОСТЬ}'. Максимальная длина: 150 символов. Используй эмодзи, сделай стиль динамичным. Добавь призыв к действию и 5 хештегов.",
    "telegram": "Ты – профессиональный Telegram-копирайтер. Напиши лаконичный, но информативный пост на языке {output_language} по этой новости: '{НОВОСТЬ}'. Длина: 200-400 символов. Без сложных фраз, только важные факты. В конце добавь 2-3 хештега.",
    "facebook": "Ты – профессиональный копирайтер. Напиши Facebook-пост на языке {output_language} по новости: '{НОВОСТЬ}'. Длина: 200-500 символов. Разбей на абзацы, добавь призыв к обсуждению и 3-4 хештега.",
    "tiktok": "Ты – креативный контент-мейкер TikTok. Создай описание к видео на языке {output_language} по новости: '{НОВОСТЬ}'. Максимум 150 символов. Минимум воды, максимум вовлечения. Добавь 4-5 трендовых хештегов.",
    "youtube": "Ты – эксперт по контенту для YouTube. Напиши описание видео на языке {output_language}, основываясь на новости: '{НОВОСТЬ}'. Длина: до 300 символов. Добавь интригу, призыв к подписке и 2-3 хештега.",
    "pinterest": "Ты – креативный копирайтер для Pinterest. Напиши описание для пина на языке {output_language} по новости: '{НОВОСТЬ}'. Длина: до 500 символов. Используй вдохновляющий стиль, добавь 3-4 хештега."
}

def extract_keywords(text):
    """Извлекает ключевые слова и фразы из текста."""
    doc = nlp(text)
    keywords = []
    for token in doc:
        # Выбираем существительные, прилагательные, имена собственные
        if token.pos_ in ("NOUN", "ADJ", "PROPN"):
            keywords.append(token.text)
    # Можно добавить фразы (chunks):
    # for chunk in doc.noun_chunks:
    #     keywords.append(chunk.text)

    return keywords

def generate_image(news_text):
    """Генерирует изображение по текстовому описанию (с извлечением ключевых слов)."""
    if not openai.api_key:
        return {"url": None, "error": "Ошибка: API-ключ OpenAI не установлен."}
    try:
        keywords = extract_keywords(news_text)
        if keywords:
          prompt = f"Изображение на тему: {', '.join(keywords[:5])}"  # Первые 5 ключевых слов
        else:
          prompt = "Новостное изображение" # Заглушка

        # client = openai.OpenAI() # Исправлено
        response = openai.images.generate( # Исправлено
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        return {"url": image_url, "error": None}
    except openai.APIError as e:
        logging.error(f"Ошибка OpenAI при генерации изображения: {e}")  # Логирование!
        return {"url": None, "error": f"Ошибка OpenAI: {e}"}
    except Exception as e:
        logging.error(f"Неизвестная ошибка при генерации изображения: {e}")  # Логирование!
        return {"url": None, "error": f"Произошла ошибка: {e}"}

def generate_social_media_text(news_text, platform, output_language):
    """Генерирует текст для соцсети."""
    prompt = PLATFORM_PROMPTS.get(platform)
    if not prompt:
        return {"text": "Платформа не поддерживается.", "success": False, "warning": None, "image_url": None} # Добавлено

    prompt = prompt.format(НОВОСТЬ=news_text, output_language=output_language)
    try:
        #client = openai.OpenAI() # Исправлено
        response = openai.chat.completions.create( # Исправлено
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты профессиональный SMM-копирайтер."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7,
        )
        generated_text = response.choices[0].message.content.strip()
        return {"text": generated_text, "success": True, "warning": None, "image_url": None} # Добавлено
    except openai.APIError as e:
        logging.error(f"Ошибка OpenAI при генерации текста: {e}")  # Логирование!
        return {"text": f"Ошибка OpenAI: {e}", "success": False, "warning": None, "image_url": None} # Добавлено
    except Exception as e:
        logging.error(f"Неизвестная ошибка при генерации текста: {e}")  # Логирование!
        return {"text": f"Произошла ошибка: {e}", "success": False, "warning": None, "image_url": None} # Добавлено


@app.route('/', methods=['GET', 'POST'])
def index():
    generated_texts = {}
    generated_image_url = None
    if request.method == 'POST':
        news_text = request.form['news_text'].strip()
        platforms = request.form.getlist('platforms')
        output_language = request.form['output_language']

        if not news_text:
            flash("Введите текст новости.", "error")
            return render_template('index.html', generated_texts=generated_texts, generated_image_url=generated_image_url)
        if not platforms:
            flash("Выберите хотя бы одну соцсеть.", "error")
            return render_template('index.html', generated_texts=generated_texts, generated_image_url=generated_image_url)

        # Генерация изображения (с обработкой ошибок)
        image_result = generate_image(news_text)  # ПЕРЕД циклом
        if image_result["error"]:
            flash(f"Ошибка при генерации изображения: {image_result['error']}", "error")  #  Выводим ошибку
        else:
            generated_image_url = image_result["url"]


        for platform in platforms:
            result = generate_social_media_text(news_text, platform, output_language)
            generated_texts[platform] = result
            if result["success"]:
                result["image_url"] = generated_image_url  # Добавляем URL *каждой* платформе

    return render_template('index.html', generated_texts=generated_texts, generated_image_url=generated_image_url)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True) # Для Heroku и других облачных сред

@app.route('/', methods=['GET', 'POST'])
def index():
    generated_texts = {}
    generated_image_url = None
    if request.method == 'POST':
        news_text = request.form['news_text'].strip()
        platforms = request.form.getlist('platforms')
        output_language = request.form['output_language']
        if not news_text:
            flash("Введите текст новости.", "error")
            return render_template('index.html', generated_texts=generated_texts, generated_image_url=generated_image_url)
        if not platforms:
            flash("Выберите хотя бы одну соцсеть.", "error")
            return render_template('index.html', generated_texts=generated_texts, generated_image_url=generated_image_url)
        image_result = generate_image(news_text)
        if not image_result["error"]:
            generated_image_url = image_result["url"]
        for platform in platforms:
            result = generate_social_media_text(news_text, platform, output_language)
            generated_texts[platform] = result
    return render_template('index.html', generated_texts=generated_texts, generated_image_url=generated_image_url)

if __name__ == '__main__':
    app.run(debug=True)

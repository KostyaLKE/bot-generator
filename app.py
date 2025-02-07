import openai
from flask import Flask, render_template, request, flash
from dotenv import load_dotenv
import os
from langdetect import detect, LangDetectException  # Импортируем langdetect
from fetch_article import fetch_article_text



load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Замените на РЕАЛЬНЫЙ секретный ключ!

openai.api_key = os.getenv('OPENAI_API_KEY')

PLATFORM_PROMPTS = {
    "twitter": """Ты – эксперт по контенту для Twitter (X).
Напиши цепляющий твит на языке {output_language} на основе следующей новости:
"{НОВОСТЬ}"

📌 Правила:
- Длина: до 200 символов
- Минимум "воды", только суть!
- Можно добавить интригу или вопрос
- Не используй сложные конструкции
- В конце добавь 2-3 хештега на языке {output_language}

🎯 Твой текст должен быть емким, но мощным!""",
    "instagram": """Ты – профессиональный SMM-копирайтер, который создает увлекательные посты для Instagram.
Твоя задача — написать пост на языке {output_language} на основе следующей новости:
"{НОВОСТЬ}"

📌 Правила оформления:
- Максимальная длина поста: 150 символов
- Стиль: динамичный, яркий, с эмоциями
- Используй эмодзи, чтобы привлечь внимание
- Добавь призыв к действию (например, "Что думаете? Делитесь в комментариях! 💬")
- В конце добавь до 5 популярных хештегов, связанных с темой, на языке {output_language}

🎯 Твой результат должен быть кратким, увлекательным и соответствовать стилистике Instagram!""",
    "facebook": """Ты – профессиональный копирайтер, который пишет посты для Facebook.
На основе следующей новости создай вовлекающий пост на языке {output_language}:
"{НОВОСТЬ}"

📌 Правила:
- Длина: 200-500 символов
- Формат: 2-3 абзаца, без сложных фраз
- Добавь призыв к обсуждению
- В конце — 3-4 хештега на языке {output_language}

🎯 Твой текст должен быть интересным и удобным для чтения!""",
    "tiktok": """Ты – креативный контент-мейкер TikTok.
Создай описание к видео на языке {output_language} на основе этой новости:
"{НОВОСТЬ}"

📌 Формат:
- Максимум 150 символов
- Минимум "воды", максимум вовлечения
- Добавь 4-5 популярных хештегов на языке {output_language}

🎯 Должно выглядеть так, будто это трендовый контент TikTok!""",
    "telegram": """Ты – профессиональный Telegram-копирайтер.
Напиши лаконичный, но информативный пост на языке {output_language} по этой новости:
"{НОВОСТЬ}"

📌 Условия:
- Длина: 200-400 символов
- Не слишком официально, но и не "жёлтая пресса"
- Важные факты + легкий намек на вывод
- 2-3 хештега в конце на языке {output_language}

🎯 Текст должен быть полезным и читабельным!""",
    "pinterest": """Ты – креативный копирайтер для Pinterest.
Создай описание для пина на языке {output_language} на основе этой новости:
"{НОВОСТЬ}"

📌 Условия:
- Длина: до 500 символов
- Используй вдохновляющий и мотивирующий стиль
- Призывай пользователей сохранять пин или делиться им
- Включи 3-4 хештега на языке {output_language}

🎯 Текст должен быть привлекательным и легко воспринимаемым!""",
    "youtube": """Ты – эксперт по контенту для YouTube.
Напиши описание видео на языке {output_language}, основываясь на следующей новости:
"{НОВОСТЬ}"

📌 Условия:
- Длина: до 300 символов
- Кратко расскажи о теме видео
- Используй интересный стиль, чтобы вовлечь зрителя
- Призови подписаться или оставить комментарий
- Добавь 2-3 хештега на языке {output_language}

🎯 Текст должен быть информативным, но с элементами интриги!"""
}

def detect_language(text):
    """Определяет язык текста."""
    try:
        return detect(text)
    except LangDetectException:
        return 'en'  # В случае ошибки возвращаем английский по умолчанию


def generate_social_media_text(news_text, platform, output_language):
    """Генерирует текст для соцсети с учетом языка."""
    prompt = PLATFORM_PROMPTS.get(platform)
    if not prompt:
        return {"text": "Платформа не поддерживается.", "success": False, "warning": None}
    
    # news_language = detect_language(news_text) #Определяем язык текста новости. (Это больше не нужно)

    prompt = prompt.format(НОВОСТЬ=news_text, output_language=output_language) #, news_language=news_language)

    if not openai.api_key:
        return {"text": "Ошибка: API-ключ OpenAI не установлен.  Установите переменную окружения OPENAI_API_KEY.", "success": False, "warning": None}

    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.7,
        )
        generated_text = response.choices[0].message.content.strip()
        return {"text": generated_text, "success": True, "warning": None}

    except openai.APIError as e:
        return {"text": f"Ошибка OpenAI: {e}", "success": False, "warning": None}
    except Exception as e:
        return {"text": f"Произошла ошибка: {e}", "success": False, "warning": None}


@app.route('/', methods=['GET', 'POST'])
def index():
    generated_texts = {}
    if request.method == 'POST':
        news_text = request.form['news_text'].strip()
        platforms = request.form.getlist('platforms')
        output_language = request.form['output_language']  # Получаем выбранный язык

        if not news_text:
            flash("Пожалуйста, введите текст новости.", "error")
            return render_template('index.html', generated_texts=generated_texts)

        if not platforms:
            flash("Пожалуйста, выберите хотя бы одну соцсеть.", "error")
            return render_template('index.html', generated_texts=generated_texts)

        for platform in platforms:
            result = generate_social_media_text(news_text, platform, output_language) # Передаём язык
            generated_texts[platform] = result

    return render_template('index.html', generated_texts=generated_texts)


if __name__ == '__main__':
    app.run(debug=True)
import openai
from flask import Flask, render_template, request, flash
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

openai.api_key = os.getenv('OPENAI_API_KEY')

PLATFORM_PROMPTS = {
    "twitter": "Ты – эксперт по контенту для Twitter (X). Напиши цепляющий твит на языке {output_language} на основе следующей новости: '{НОВОСТЬ}'. Длина: до 200 символов. Минимум 'воды', только суть! Можно добавить интригу или вопрос. В конце добавь 2-3 хештега.",
    "instagram": "Ты – профессиональный SMM-копирайтер. Напиши увлекательный Instagram-пост на языке {output_language} по новости: '{НОВОСТЬ}'. Максимальная длина: 150 символов. Используй эмодзи, сделай стиль динамичным. Добавь призыв к действию и 5 хештегов.",
    "telegram": "Ты – профессиональный Telegram-копирайтер. Напиши лаконичный, но информативный пост на языке {output_language} по этой новости: '{НОВОСТЬ}'. Длина: 200-400 символов. Без сложных фраз, только важные факты. В конце добавь 2-3 хештега.",
    "facebook": "Ты – профессиональный копирайтер. Напиши Facebook-пост на языке {output_language} по новости: '{НОВОСТЬ}'. Длина: 200-500 символов. Разбей на абзацы, добавь призыв к обсуждению и 3-4 хештега.",
    "tiktok": "Ты – креативный контент-мейкер TikTok. Создай описание к видео на языке {output_language} по новости: '{НОВОСТЬ}'. Максимум 150 символов. Минимум воды, максимум вовлечения. Добавь 4-5 трендовых хештегов.",
    "youtube": "Ты – эксперт по контенту для YouTube. Напиши описание видео на языке {output_language}, основываясь на новости: '{НОВОСТЬ}'. Длина: до 300 символов. Добавь интригу, призыв к подписке и 2-3 хештега.",
    "pinterest": "Ты – креативный копирайтер для Pinterest. Напиши описание для пина на языке {output_language} по новости: '{НОВОСТЬ}'. Длина: до 500 символов. Используй вдохновляющий стиль, добавь 3-4 хештега."
}

def generate_image(news_text):
    """Генерирует изображение по текстовому описанию."""
    if not openai.api_key:
        return {"url": None, "error": "Ошибка: API-ключ OpenAI не установлен."}
    try:
        client = openai.OpenAI()
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"Иллюстрация по новости: {news_text}",
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        return {"url": image_url, "error": None}
    except openai.APIError as e:
        return {"url": None, "error": f"Ошибка OpenAI: {e}"}
    except Exception as e:
        return {"url": None, "error": f"Произошла ошибка: {e}"}

def generate_social_media_text(news_text, platform, output_language):
    """Генерирует текст для соцсети."""
    prompt = PLATFORM_PROMPTS.get(platform)
    if not prompt:
        return {"text": "Платформа не поддерживается.", "success": False, "warning": None}
    prompt = prompt.format(НОВОСТЬ=news_text, output_language=output_language)
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты профессиональный SMM-копирайтер."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
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

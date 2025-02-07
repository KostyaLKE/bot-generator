import openai
from flask import Flask, render_template, request, flash
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

openai.api_key = os.getenv('OPENAI_API_KEY')

PLATFORM_PROMPTS = {  # Добавим заглушки для промптов, чтобы не было ошибки
    "twitter": "Твит для новости: {НОВОСТЬ}",
    "instagram": "Пост для Instagram: {НОВОСТЬ}",
    "telegram": "Пост для Telegram: {НОВОСТЬ}",
    "facebook": "Пост для Facebook: {НОВОСТЬ}",
    "tiktok": "Описание для TikTok: {НОВОСТЬ}",
    "youtube": "Описание для YouTube: {НОВОСТЬ}",
    "pinterest": "Описание для Pinterest: {НОВОСТЬ}",
}

def generate_image(prompt):
    """Генерирует изображение по текстовому описанию."""
    if not openai.api_key:
        return {"url": None, "error": "Ошибка: API-ключ OpenAI не установлен."}
    try:
        client = openai.OpenAI()
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
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
    """Генерирует текст для соцсети (упрощенная версия)."""
    prompt = PLATFORM_PROMPTS.get(platform)
    if not prompt:
        return {"text": "Платформа не поддерживается.", "success": False, "warning": None}

    prompt = prompt.format(НОВОСТЬ=news_text) # Подставляем новость в простейший промпт

    if not openai.api_key:
        return {"text": "Ошибка: API-ключ OpenAI не установлен.", "success": False, "warning": None}

    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Или gpt-4-turbo
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,  # Увеличим немного
            temperature=0.7,
        )
        generated_text = response.choices[0].message.content.strip()

        # Добавляем перевод, если язык не английский (простейший пример)
        if output_language != "en":
          translation_prompt = f"Translate the following text to {output_language}: {generated_text}"
          translation_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                {"role": "system", "content": "You are a helpful translator."},
                {"role": "user", "content": translation_prompt}
              ]
          )
          generated_text = translation_response.choices[0].message.content.strip()

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
            flash("Пожалуйста, введите текст новости.", "error")
            return render_template('index.html', generated_texts=generated_texts, generated_image_url=generated_image_url)

        if not platforms:
            flash("Пожалуйста, выберите хотя бы одну соцсеть.", "error")
            return render_template('index.html', generated_texts=generated_texts, generated_image_url=generated_image_url)

        # Генерация изображения
        image_result = generate_image(news_text)  # Используем текст новости как промпт для изображения
        if image_result["error"]:
            flash(image_result["error"], "error")
            #  Если ошибка с изображением, все равно генерируем текст
        else:
            generated_image_url = image_result["url"]

        # Генерация текста для соцсетей
        for platform in platforms:
            result = generate_social_media_text(news_text, platform, output_language)
            generated_texts[platform] = result

    return render_template('index.html', generated_texts=generated_texts, generated_image_url=generated_image_url)

if __name__ == '__main__':
    app.run(debug=True)
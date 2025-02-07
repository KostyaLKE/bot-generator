import openai
from flask import Flask, render_template, request, flash
from dotenv import load_dotenv
import os
import re
import logging
from collections import defaultdict

# Загрузка переменных окружения
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')

# Настройка логирования
logging.basicConfig(level=logging.ERROR, filename="app_errors.log", format='%(asctime)s - %(levelname)s - %(message)s')

# Загружаем API-ключ OpenAI при старте приложения
openai.api_key = os.getenv('OPENAI_API_KEY')
if not openai.api_key:
    raise ValueError("API-ключ OpenAI не установлен! Установите переменную окружения OPENAI_API_KEY.")

PLATFORM_PROMPTS = {
    "twitter": """Ты – эксперт по контенту для Twitter (X).
Напиши цепляющий твит на языке {output_language} на основе следующей новости:
"{НОВОСТЬ}"
... (остальной код без изменений) ...
"""
}

def generate_image(prompt):
    """Генерирует изображение по текстовому описанию."""
    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        return {"url": response.data[0].url, "error": None}

    except openai.APIError as e:
        logging.error(f"Ошибка OpenAI при генерации изображения: {e}")
        return {"url": None, "error": f"Ошибка OpenAI: {e}"}
    except Exception as e:
        logging.error(f"Неизвестная ошибка при генерации изображения: {e}")
        return {"url": None, "error": f"Произошла ошибка: {e}"}

def generate_social_media_post(news_text, platform, output_language):
    """Генерирует текст поста и промпт для изображения."""
    prompt_template = PLATFORM_PROMPTS.get(platform)
    if not prompt_template:
        return {"text": "Платформа не поддерживается.", "image_prompt": None, "success": False, "warning": None}

    prompt = prompt_template.format(НОВОСТЬ=news_text, output_language=output_language)

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=700,
            temperature=0.7,
        )
        full_response = response.choices[0].message.content.strip()

        match = re.search(r'📷 Промпт для изображения:\s*(.*)', full_response, re.DOTALL)
        image_prompt = match.group(1).strip().strip('"') if match else None

        text_match = re.search(r'(.*?)(🔹 Теперь сгенерируй|📷 Промпт для изображения:)', full_response, re.DOTALL)
        post_text = text_match.group(1).strip() if text_match else full_response

        return {"text": post_text, "image_prompt": image_prompt, "success": True, "warning": None}

    except openai.APIError as e:
        logging.error(f"Ошибка OpenAI при генерации текста: {e}")
        return {"text": f"Ошибка OpenAI: {e}", "image_prompt": None, "success": False, "warning": None}
    except Exception as e:
        logging.error(f"Неизвестная ошибка при генерации текста: {e}")
        return {"text": f"Произошла ошибка: {e}", "image_prompt": None, "success": False, "warning": None}

@app.route('/', methods=['GET', 'POST'])
def index():
    """Основная логика приложения."""
    generated_texts = {}
    if request.method == 'POST':
        news_text = request.form['news_text'].strip()
        platforms = request.form.getlist('platforms')
        output_language = request.form['output_language']

        if not news_text or not platforms:
            flash("Введите текст новости и выберите соцсеть.", "error")
            return render_template('index.html', generated_texts={})

        for platform in platforms:
            result = generate_social_media_post(news_text, platform, output_language)
            if result["success"]:
                if result["image_prompt"]:
                    image_result = generate_image(result["image_prompt"])
                    result["image_url"] = image_result["url"]
                    if image_result["error"]:
                        flash(f"Ошибка изображения ({platform}): {image_result['error']}", "error")
            generated_texts[platform] = result

    return render_template('index.html', generated_texts=generated_texts)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)

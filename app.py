import openai
from flask import Flask, render_template, request, flash
from dotenv import load_dotenv
import os
import re  # Импортируем модуль для регулярных выражений

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

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

🎯 Твой текст должен быть емким, но мощным!

🔹 Теперь сгенерируй изображение для поста.
Оно должно отражать основную идею новости и быть визуально привлекательным.

📷 Промпт для изображения:
"Фотореалистичное изображение {ключевая_деталь}, в стиле {атмосфера}, фон {окружение}, {доп_детали}, кинематографическое освещение, высокая детализация."
""",
    "instagram": """Ты – профессиональный SMM-копирайтер, который создает увлекательные посты для Instagram.
Твоя задача — написать пост на языке {output_language} на основе следующей новости:
"{НОВОСТЬ}"

📌 Правила оформления:
- Максимальная длина поста: 150 символов
- Стиль: динамичный, яркий, с эмоциями
- Используй эмодзи, чтобы привлечь внимание
- Добавь призыв к действию (например, "Что думаете? Делитесь в комментариях! 💬")
- В конце добавь до 5 популярных хештегов, связанных с темой, на языке {output_language}

🎯 Твой результат должен быть кратким, увлекательным и соответствовать стилистике Instagram!

🔹 Теперь сгенерируй изображение, которое идеально подойдет для Instagram-поста.

📷 Промпт для изображения:
"Красочное и стильное изображение {ключевой_объект}, акцент на {деталь}, современный инстаграммный стиль, мягкое освещение, яркие цвета, идеально подходит для соцсетей."
""",
    "facebook": """Ты – профессиональный копирайтер, который пишет посты для Facebook.
На основе следующей новости создай вовлекающий пост на языке {output_language}:
"{НОВОСТЬ}"

📌 Правила:
- Длина: 200-500 символов
- Формат: 2-3 абзаца, без сложных фраз
- Добавь призыв к обсуждению
- В конце — 3-4 хештега на языке {output_language}

🎯 Твой текст должен быть интересным и удобным для чтения!

🔹 Теперь сгенерируй изображение, которое привлечет внимание в ленте Facebook.

📷 Промпт для изображения:
"Фотореалистичное изображение {главный_объект}, естественное освещение, сочные цвета, композиция с акцентом на {ключевой_элемент}, социальный контекст, приятный глазу фон."
""",
    "tiktok": """Ты – креативный контент-мейкер TikTok.
Создай описание к видео на языке {output_language} на основе этой новости:
"{НОВОСТЬ}"

📌 Формат:
- Максимум 150 символов
- Минимум "воды", максимум вовлечения
- Добавь 4-5 популярных хештегов на языке {output_language}

🎯 Должно выглядеть так, будто это трендовый контент TikTok!

🔹 Теперь сгенерируй стильное изображение-обложку для видео.

📷 Промпт для изображения:
"Яркое, динамичное изображение {ключевой_объект}, акцент на {главная_эмоция}, трендовый стиль, неоновая подсветка, современный молодежный дизайн, захватывающий ракурс."
""",
    "telegram": """Ты – профессиональный Telegram-копирайтер.
Напиши лаконичный, но информативный пост на языке {output_language} по этой новости:
"{НОВОСТЬ}"

📌 Условия:
- Длина: 200-400 символов
- Не слишком официально, но и не "жёлтая пресса"
- Важные факты + легкий намек на вывод
- 2-3 хештега в конце на языке {output_language}

🎯 Текст должен быть полезным и читабельным!

🔹 Теперь создай изображение, которое хорошо дополнит новость в Telegram.

📷 Промпт для изображения:
"Минималистичное, но выразительное изображение {ключевой_объект}, акцент на {деталь}, контрастные цвета, легкость в восприятии, современный новостной стиль."
""",
    "pinterest": """Ты – креативный копирайтер для Pinterest.
Создай описание для пина на языке {output_language} на основе этой новости:
"{НОВОСТЬ}"

📌 Условия:
- Длина: до 500 символов
- Используй вдохновляющий и мотивирующий стиль
- Призывай пользователей сохранять пин или делиться им
- Включи 3-4 хештега на языке {output_language}

🎯 Текст должен быть привлекательным и легко воспринимаемым!

🔹 Теперь создай привлекательное изображение для Pinterest.

📷 Промпт для изображения:
"Эстетичное изображение {ключевой_объект}, нежные цвета, стиль lifestyle, идеальная композиция, вдохновляющая атмосфера, трендовый визуал, аккуратные детали."
""",
    "youtube": """Ты – эксперт по контенту для YouTube.
Напиши описание видео на языке {output_language}, основываясь на следующей новости:
"{НОВОСТЬ}"

📌 Условия:
- Длина: до 300 символов
- Кратко расскажи о теме видео
- Используй интересный стиль, чтобы вовлечь зрителя
- Призови подписаться или оставить комментарий
- Добавь 2-3 хештега на языке {output_language}

🎯 Текст должен быть информативным, но с элементами интриги!

🔹 Теперь сгенерируй изображение-обложку для видео.

📷 Промпт для изображения:
"Яркая, броская обложка YouTube, {ключевой_объект}, крупный шрифт с интригующим заголовком, контрастные цвета, динамичный фон, профессиональная графика."
"""
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

def generate_social_media_post(news_text, platform, output_language):
    """Генерирует текст поста и промпт для изображения."""
    prompt_template = PLATFORM_PROMPTS.get(platform)
    if not prompt_template:
        return {"text": "Платформа не поддерживается.", "image_prompt": None, "success": False, "warning": None}

    # Форматируем ТОЛЬКО новость и язык в *основном* промпте
    prompt = prompt_template.format(НОВОСТЬ=news_text, output_language=output_language)

    if not openai.api_key:
         return {"text": "Ошибка: API-ключ OpenAI не установлен.", "image_prompt": None, "success": False, "warning": None}

    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=700,
            temperature=0.7,
        )
        full_response = response.choices[0].message.content.strip()

        # Извлекаем промпт для изображения
        match = re.search(r'📷 Промпт для изображения:\s*"(.*?)"', full_response, re.DOTALL)
        if match:
            image_prompt = match.group(1).strip()
            #  Заменяем плейсхолдеры ПОСЛЕ извлечения (простейший вариант)
            image_prompt = image_prompt.format(
              ключевая_деталь="деталь из новости",
              атмосфера="атмосфера",
              окружение="окружение",
              доп_детали="детали",
              ключевой_объект="объект",
              деталь="деталь",
              главный_объект = "объект",
              ключевой_элемент = "элемент",
              главная_эмоция = "эмоция"
            )
        else:
            image_prompt = None

        # Текст поста
        text_match = re.search(r'(.*?)(🔹 Теперь сгенерируй|📷 Промпт для изображения:)', full_response, re.DOTALL)
        if text_match:
            post_text = text_match.group(1).strip()
        else:
            post_text = full_response

        return {"text": post_text, "image_prompt": image_prompt, "success": True, "warning": None}

    except openai.APIError as e:
        return {"text": f"Ошибка OpenAI: {e}", "image_prompt": None, "success": False, "warning": None}
    except Exception as e:
        return {"text": f"Произошла ошибка: {e}", "image_prompt": None, "success": False, "warning": None}

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

        for platform in platforms:
            result = generate_social_media_post(news_text, platform, output_language)
            generated_texts[platform] = result

            # Генерация изображения
            if result["image_prompt"]:
                image_result = generate_image(result["image_prompt"])
                if image_result["error"]:
                    flash(f"Ошибка при генерации изображения для {platform}: {image_result['error']}", "error")
                else:
                    generated_texts[platform]["image_url"] = image_result["url"]
            else:
                generated_texts[platform]["image_url"] = None

    return render_template('index.html', generated_texts=generated_texts, generated_image_url=generated_image_url)

if __name__ == '__main__':
    app.run(debug=True)
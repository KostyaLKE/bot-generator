import openai
from flask import Flask, render_template, request, flash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Замените на реальный секретный ключ!
openai.api_key = 'YOUR_OPENAI_API_KEY'  # !!! Замените на ВАШ API-ключ OpenAI !!!

PLATFORM_PROMPTS = {
    "twitter": """Ты – эксперт по контенту для Twitter (X).
Напиши цепляющий твит на основе следующей новости:
"{НОВОСТЬ}"

📌 Правила:
- Длина: до 200 символов
- Минимум "воды", только суть!
- Можно добавить интригу или вопрос
- Не используй сложные конструкции
- В конце добавь 2-3 хештега

🎯 Твой текст должен быть емким, но мощным!""",
    "instagram": """Ты – профессиональный SMM-копирайтер, который создает увлекательные посты для Instagram.
Твоя задача — написать пост на основе следующей новости:
"{НОВОСТЬ}"

📌 Правила оформления:
- Максимальная длина поста: 150 символов
- Стиль: динамичный, яркий, с эмоциями
- Используй эмодзи, чтобы привлечь внимание
- Добавь призыв к действию (например, "Что думаете? Делитесь в комментариях! 💬")
- В конце добавь до 5 популярных хештегов, связанных с темой

🎯 Твой результат должен быть кратким, увлекательным и соответствовать стилистике Instagram!""",
    "facebook": """Ты – профессиональный копирайтер, который пишет посты для Facebook.
На основе следующей новости создай вовлекающий пост:
"{НОВОСТЬ}"

📌 Правила:
- Длина: 200-500 символов
- Формат: 2-3 абзаца, без сложных фраз
- Добавь призыв к обсуждению
- В конце — 3-4 хештега

🎯 Твой текст должен быть интересным и удобным для чтения!""",
    "tiktok": """Ты – креативный контент-мейкер TikTok.
Создай описание к видео на основе этой новости:
"{НОВОСТЬ}"

📌 Формат:
- Максимум 150 символов
- Минимум "воды", максимум вовлечения
- Добавь 4-5 популярных хештегов

🎯 Должно выглядеть так, будто это трендовый контент TikTok!""",
    "telegram": """Ты – профессиональный Telegram-копирайтер.
Напиши лаконичный, но информативный пост по этой новости:
"{НОВОСТЬ}"

📌 Условия:
- Длина: 200-400 символов
- Не слишком официально, но и не "жёлтая пресса"
- Важные факты + легкий намек на вывод
- 2-3 хештега в конце

🎯 Текст должен быть полезным и читабельным!""",
    "pinterest": """Ты – креативный копирайтер для Pinterest.
Создай описание для пина на основе этой новости:
"{НОВОСТЬ}"

📌 Условия:
- Длина: до 500 символов
- Используй вдохновляющий и мотивирующий стиль
- Призывай пользователей сохранять пин или делиться им
- Включи 3-4 хештега

🎯 Текст должен быть привлекательным и легко воспринимаемым!""",
    "youtube": """Ты – эксперт по контенту для YouTube.
Напиши описание видео, основываясь на следующей новости:
"{НОВОСТЬ}"

📌 Условия:
- Длина: до 300 символов
- Кратко расскажи о теме видео
- Используй интересный стиль, чтобы вовлечь зрителя
- Призови подписаться или оставить комментарий
- Добавь 2-3 хештега

🎯 Текст должен быть информативным, но с элементами интриги!"""
}

def generate_social_media_text(news_text, platform):
    prompt = PLATFORM_PROMPTS.get(platform)
    if not prompt:
        return {"text": "Платформа не поддерживается.", "success": False, "warning": None}

    prompt = prompt.format(НОВОСТЬ=news_text) # Подставляем новость в промпт

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",  #  Или gpt-3.5-turbo, если нет доступа к gpt-4
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,  #  Максимальное количество токенов (примерно соответствует длине текста)
            temperature=0.7,  #  Параметр "креативности" (0.0 - детерминированный, 1.0 - очень случайный)
        )
        generated_text = response.choices[0].message.content.strip()
        return {"text": generated_text, "success": True, "warning": None}
    except openai.error.OpenAIError as e:
        return {"text": f"Ошибка OpenAI: {e}", "success": False, "warning": None}
    except Exception as e:  # Обработка других возможных ошибок
        return {"text": f"Произошла ошибка: {e}", "success": False, "warning": None}

@app.route('/', methods=['GET', 'POST'])
def index():
    generated_texts = {}
    if request.method == 'POST':
        news_text = request.form['news_text'].strip()
        platforms = request.form.getlist('platforms')

        if not news_text:
            flash("Пожалуйста, введите текст новости.", "error")
            return render_template('index.html', generated_texts=generated_texts)

        if not platforms:
            flash("Пожалуйста, выберите хотя бы одну соцсеть.", "error")
            return render_template('index.html', generated_texts=generated_texts)

        for platform in platforms:
            result = generate_social_media_text(news_text, platform)
            generated_texts[platform] = result

    return render_template('index.html', generated_texts=generated_texts)

if __name__ == '__main__':
    app.run(debug=True)
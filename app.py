from flask import Flask, render_template, request, flash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Замените на реальный секретный ключ!

PLATFORM_CONFIG = {
    "twitter": {
        "prefix": "🚀 ",
        "suffix": " #BreakingNews",
        "max_length": 280,
        "template": lambda text, config: f"{config['prefix']}{text[:config['max_length'] - len(config['prefix']) - len(config['suffix'])]}{config['suffix']}"
    },
    "instagram": {
        "prefix": "📸 ",
        "suffix": "\n\n#news #trending #instagood",
        "template": lambda text, config: f"{config['prefix']}{text}{config['suffix']}"
    },
    "telegram": {
        "prefix": "🔹 ",
        "suffix": "\n\n📢 Подписывайтесь на канал!",
        "template": lambda text, config: f"{config['prefix']}{text}{config['suffix']}"
    },
    "facebook": {
        "prefix": "📰 ",
        "suffix": "\n\n#news #facebook",
        "template": lambda text, config: f"{config['prefix']}{text}{config['suffix']}"
    },
    "tiktok": {
        "prefix": "🎵 ",  # Префикс для TikTok
        "suffix": "\n\n#news #foryou #fyp",  # Суффикс для TikTok
        "template": lambda text, config: f"{config['prefix']}{text}{config['suffix']}"
    },
    "youtube": {
        "prefix": "▶️ ",  # Префикс для YouTube
        "suffix": "\n\n#news #video #youtube",  # Суффикс для YouTube
         "template": lambda text, config: f"{config['prefix']}{text}{config['suffix']}"
    },
    "pinterest": {
        "prefix": "📌 ",  # Префикс для Pinterest
        "suffix": "\n\n#news #pin #pinterest",  # Суффикс для Pinterest
        "template": lambda text, config: f"{config['prefix']}{text}{config['suffix']}"
    },
    # LinkedIn удален
}

def generate_social_media_text(news_text, platform):
    config = PLATFORM_CONFIG.get(platform)
    if not config:
        return {"text": "Платформа не поддерживается.", "success": False, "warning": None}

    generated_text = config['template'](news_text, config)
    warning = None
    if platform == "twitter" and len(news_text) > config['max_length'] - len(config['prefix']) - len(config['suffix']):
        warning = "Текст новости был обрезан для Twitter."

    return {"text": generated_text, "success": True, "warning": warning}



@app.route('/', methods=['GET', 'POST'])
def index():
    generated_texts = {}  # Словарь для хранения результатов
    if request.method == 'POST':
        news_text = request.form['news_text'].strip()
        platforms = request.form.getlist('platforms')  # Получаем СПИСОК выбранных платформ

        if not news_text:
            flash("Пожалуйста, введите текст новости.", "error")
            return render_template('index.html', generated_texts=generated_texts)

        if not platforms:
            flash("Пожалуйста, выберите хотя бы одну соцсеть.", "error")
            return render_template('index.html', generated_texts=generated_texts)


        for platform in platforms:
            result = generate_social_media_text(news_text, platform)
            if result["success"]:
                generated_texts[platform] = result # Сохраняем результат в словаре
            else:
                flash(result["text"], "error") # Если ошибка для платформы

    return render_template('index.html', generated_texts=generated_texts)


if __name__ == '__main__':
    app.run(debug=True)
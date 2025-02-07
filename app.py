from flask import Flask, render_template, request, flash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Секретный ключ для flash-сообщений.  Замените на реальный!

# Константы
PLATFORM_CONFIG = {
    "twitter": {
        "prefix": "🚀 ",
        "suffix": " #BreakingNews",
        "max_length": 280,  # Максимальная длина твита (включая префикс и суффикс).  280 - стандартная длина.
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
}

DEFAULT_PLATFORM = "twitter"  # Платформа по умолчанию

def generate_social_media_text(news_text, platform):
    config = PLATFORM_CONFIG.get(platform)
    if not config:
        return "Платформа не поддерживается.", False  # Возвращаем кортеж: (текст, успех)

    generated_text = config['template'](news_text, config)
    return generated_text, True

@app.route('/', methods=['GET', 'POST'])
def index():
    generated_text = ""
    if request.method == 'POST':
        news_text = request.form['news_text'].strip()  # Удаляем пробелы в начале и конце
        platform = request.form['platform']

        if not news_text:
            flash("Пожалуйста, введите текст новости.", "error") # Используем flash сообщения
            return render_template('index.html', generated_text=generated_text)
        
        text, success = generate_social_media_text(news_text, platform)
        if success:
            generated_text = text
            if platform == "twitter" and len(news_text) > PLATFORM_CONFIG["twitter"]["max_length"] - len(PLATFORM_CONFIG["twitter"]["prefix"]) - len(PLATFORM_CONFIG["twitter"]["suffix"]):
              flash("Текст новости был обрезан для Twitter.", "warning")
        else:
            flash(text, "error")  # text содержит "Платформа не поддерживается."

    return render_template('index.html', generated_text=generated_text)

if __name__ == '__main__':
    app.run(debug=True)
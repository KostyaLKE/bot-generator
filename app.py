from flask import Flask, render_template, request

app = Flask(__name__)

# Функция генерации текста под соцсеть
def generate_social_media_text(news_text, platform):
    if platform == "twitter":
        return f"🚀 {news_text[:240]}... #BreakingNews"
    elif platform == "instagram":
        return f"📸 {news_text}\n\n#news #trending #instagood"
    elif platform == "telegram":
        return f"🔹 {news_text}\n\n📢 Подписывайтесь на канал!"
    else:
        return "Платформа не поддерживается."

@app.route('/', methods=['GET', 'POST'])
def index():
    generated_text = ""
    if request.method == 'POST':
        news_text = request.form['news_text']
        platform = request.form['platform']
        generated_text = generate_social_media_text(news_text, platform)
    return render_template('index.html', generated_text=generated_text)

if __name__ == '__main__':
    app.run(debug=True)

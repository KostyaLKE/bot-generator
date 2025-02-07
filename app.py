from flask import Flask, render_template, request
import random

app = Flask(__name__)

# Функция генерации хештегов по ключевым словам
def generate_hashtags(text):
    words = text.lower().split()
    common_tags = ["news", "update", "breaking", "trending", "socialmedia"]
    hashtags = ["#" + word for word in words if len(word) > 4][:3] + ["#" + tag for tag in random.sample(common_tags, 2)]
    return " ".join(hashtags)

# Функция генерации текста под соцсеть с учетом стиля
def generate_social_media_text(news_text, platform, style):
    hashtags = generate_hashtags(news_text)
    
    if style == "formal":
        news_text = f"Важная новость: {news_text}"  
    elif style == "informal":
        news_text = f"🔥 Чувак, смотри что случилось! {news_text}"  
    
    if platform == "twitter":
        return f"🚀 {news_text[:240]}... {hashtags}"
    elif platform == "instagram":
        return f"📸 {news_text}\n\n{hashtags}"
    elif platform == "telegram":
        return f"🔹 {news_text}\n\n📢 Подписывайтесь на канал!"
    elif platform == "facebook":
        return f"📢 {news_text}\n\n{hashtags}"
    elif platform == "linkedin":
        return f"💼 {news_text}\n\n#ProfessionalNews"
    elif platform == "tiktok":
        return f"🎵 {news_text} 🔥 {hashtags}"
    elif platform == "youtube":
        return f"🎬 {news_text}\n\n{hashtags}"
    else:
        return "Платформа не поддерживается."

@app.route('/', methods=['GET', 'POST'])
def index():
    generated_text = ""
    if request.method == 'POST':
        news_text = request.form['news_text']
        platform = request.form['platform']
        style = request.form['style']
        generated_text = generate_social_media_text(news_text, platform, style)
    return render_template('index.html', generated_text=generated_text)

if __name__ == '__main__':
    app.run(debug=True)

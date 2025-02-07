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
    elif style == "friendly":
        news_text = f"😊 Привет, друзья! Вот что произошло: {news_text}"
    elif style == "professional":
        news_text = f"📢 Официальное заявление: {news_text}"
    elif style == "sarcastic":
        news_text = f"🙃 О, ну конечно, ещё одна "замечательная" новость... {news_text}"
    
    templates = {
        "twitter": f"🚀 {news_text[:240]}... {hashtags}",
        "instagram": f"📸 {news_text}\n\n{hashtags}",
        "telegram": f"🔹 {news_text}\n\n📢 Подписывайтесь на канал!",
        "facebook": f"📢 {news_text}\n\n{hashtags}",
        "linkedin": f"💼 {news_text}\n\n#ProfessionalNews",
        "tiktok": f"🎵 {news_text} 🔥 {hashtags}",
        "youtube": f"🎬 {news_text}\n\n{hashtags}"
    }
    
    return templates.get(platform, "Платформа не поддерживается.")

@app.route('/', methods=['GET', 'POST'])
def index():
    generated_texts = {}
    if request.method == 'POST':
        news_text = request.form['news_text']
        platforms = request.form.getlist('platforms')
        style = request.form['style']
        
        for platform in platforms:
            generated_texts[platform] = generate_social_media_text(news_text, platform, style)
    
    return render_template('index.html', generated_texts=generated_texts)

if __name__ == '__main__':
    app.run(debug=True)

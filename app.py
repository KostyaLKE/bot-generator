from flask import Flask, render_template, request, send_file
import instaloader
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip
import os
import shutil
from openai import OpenAI

app = Flask(__name__)

# Инициализация Instaloader и OpenAI
L = instaloader.Instaloader()
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here")
)  # Убраны дополнительные параметры вроде proxies

# Функция для парсинга поста
def parse_instagram_post(url):
    try:
        shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        L.download_post(post, target="downloaded_post")
        content_type = "image" if not post.is_video else "video"
        content_path = f"downloaded_post/{post.shortcode}.jpg" if content_type == "image" else f"downloaded_post/{post.shortcode}.mp4"
        caption = post.caption if post.caption else "Без текста"
        return content_type, content_path, caption
    except Exception as e:
        return None, None, f"Ошибка парсинга: {str(e)}"

# Генерация текста через OpenAI
def generate_text(original_text, text_changes):
    prompt = f"Перепиши следующий текст с учетом этих изменений: '{text_changes}'. Оригинальный текст: '{original_text}'"
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100
    )
    return response.choices[0].message.content.strip()

# Генерация изображения через OpenAI (DALL·E)
def generate_image(description):
    response = openai_client.images.generate(
        model="dall-e-3",
        prompt=description,
        n=1,
        size="1024x1024"
    )
    image_url = response.data[0].url
    image_path = f"static/generated_image_{len(os.listdir('static'))}.jpg"
    with open(image_path, "wb") as f:
        f.write(requests.get(image_url).content)
    return image_path

# Функция для изменения изображения (если не генерируем новое)
def edit_image(image_path, changes):
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.text((10, 10), changes, font=font, fill=(255, 0, 0))
    new_path = f"static/edited_image_{os.path.basename(image_path)}"
    img.save(new_path)
    return new_path

# Функция для изменения видео
def edit_video(video_path, changes):
    clip = VideoFileClip(video_path)
    new_clip = clip.subclip(0, min(10, clip.duration))
    new_path = f"static/edited_video_{os.path.basename(video_path)}"
    new_clip.write_videofile(new_path, logger=None)
    return new_path

# Генерация постов
def generate_posts(content_type, content_path, text, changes, text_changes, num_posts):
    results = []
    for i in range(num_posts):
        # Генерируем новый текст
        new_text = generate_text(text, text_changes) + f" (Пост #{i+1})"
        
        if content_type == "image":
            if "сгенерировать новое" in changes.lower():
                new_content = generate_image(changes + f" Пост #{i+1}")
            else:
                new_content = edit_image(content_path, changes + f" Пост #{i+1}")
        else:
            new_content = edit_video(content_path, changes)
        
        results.append((new_content, new_text))
    return results

# Главная страница
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]
        changes = request.form["changes"]
        text_changes = request.form["text_changes"]
        num_posts = int(request.form["num_posts"])

        # Очищаем старые файлы
        if os.path.exists("downloaded_post"):
            shutil.rmtree("downloaded_post")
        if os.path.exists("static"):
            for f in os.listdir("static"):
                if f != "style.css":
                    os.remove(os.path.join("static", f))

        # Парсинг и генерация
        content_type, content_path, caption = parse_instagram_post(url)
        if content_path:
            results = generate_posts(content_type, content_path, caption, changes, text_changes, num_posts)
            return render_template("index.html", results=results, error=None)
        else:
            return render_template("index.html", results=None, error=caption)
    
    return render_template("index.html", results=None, error=None)

if __name__ == "__main__":
    if not os.path.exists("static"):
        os.makedirs("static")
    app.run(host="0.0.0.0", port=5000)
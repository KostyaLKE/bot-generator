from flask import Flask, send_from_directory
from .routes import text_routes, image_routes, video_routes, youtube_routes # Точка перед routes
from .config import Config  # <- ИЗМЕНЕНИЕ: Точка перед config

app = Flask(__name__, static_folder='../public', static_url_path='/')
app.config.from_object(Config)

# ... (регистрация маршрутов)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html') # Отдаем index.html


if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
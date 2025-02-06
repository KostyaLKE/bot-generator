from flask import Flask, send_from_directory  # Добавь send_from_directory
from src.routes import text_routes, image_routes, video_routes, youtube_routes  # ... (остальные импорты)
from src.config import Config

app = Flask(__name__, static_folder='../public', static_url_path='/')  # ИЗМЕНЕНИЯ!
app.config.from_object(Config)

# ... (регистрация маршрутов)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html') # Отдаем index.html


if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
# bot-generator-main/src/app.py

from flask import Flask, send_from_directory
from src.routes import text_routes, image_routes, video_routes, youtube_routes  # Импортируй все роуты
from src.config import Config

app = Flask(__name__, static_folder='../public', static_url_path='/')
app.config.from_object(Config)

# Регистрация маршрутов
app.register_blueprint(text_routes.text_bp, url_prefix='/api/text')
app.register_blueprint(image_routes.image_bp, url_prefix='/api/image')
app.register_blueprint(video_routes.video_bp, url_prefix='/api/video')
app.register_blueprint(youtube_routes.youtube_bp, url_prefix='/api/youtube')

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
from flask import Blueprint
from src.controllers import text_controller

text_bp = Blueprint('text', __name__)

text_bp.route('/generate', methods=['POST'])(text_controller.generate_text_from_news)
# Другие маршруты для текста...
from flask import Blueprint
from src.controllers import text_controller

text_bp = Blueprint('text', __name__)

# Убедись, что methods=['POST'] указан!
text_bp.route('/generate', methods=['POST'])(text_controller.generate_text_from_news)
from flask import Blueprint
# from src.controllers import image_controller  # Раскомментируй, когда создашь контроллер

image_bp = Blueprint('image', __name__)  # <- СОЗДАЙ Blueprint с именем image_bp

# @image_bp.route('/generate', methods=['POST']) # Раскомментируй и создай функцию, когда будешь готов
# def generate_image():
#     # ... Логика генерации изображения ...
#     pass
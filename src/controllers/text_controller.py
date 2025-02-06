# bot-generator-main/src/controllers/text_controller.py

from flask import request, jsonify, Blueprint
from src.services.text_generation.text_service import text_service  #  Импортируем text_service


def generate_text_from_news():
    try:
        # data = request.get_json() #Устарело
        # Вместо request.get_json()
        news_text = request.form.get('newsText') # Текст
        social_networks = request.form.getlist('socialNetworks') # Список соц. сетей
        other_name = request.form.get('otherName')
        action = request.form.get('action')

        #Тут оставим вызов генерации текста
        if action == "generate_text":
            generated_texts = text_service.generate_text_for_social_media(news_text, social_networks, other_name)
            return jsonify(generated_texts), 200


    except Exception as e:
        print(f"Error in text_controller: {e}")
        return jsonify({'error': 'Text generation failed'}), 500
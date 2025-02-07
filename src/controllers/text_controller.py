# src/controllers/text_controller.py

from flask import request, jsonify, Blueprint
from src.services.text_generation.simple_test import test_openai  # Импортируем новую функцию


def generate_text_from_news():
    try:
        #  Временно используем простую функцию
        result = test_openai()
        return jsonify({"result": result}), 200


    except Exception as e:
        print(f"Error in text_controller: {e}")
        return jsonify({'error': 'Text generation failed'}), 500
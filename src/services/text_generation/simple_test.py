# src/services/text_generation/simple_test.py

import openai
from src.config import Config

def test_openai():
    """
    Простая функция для проверки работы OpenAI API.
    """
    openai.api_key = Config.OPENAI_API_KEY
    if not openai.api_key:
        return "OPENAI_API_KEY is not set"

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-instruct",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say this is a test."},
            ],
            max_tokens=10,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"OpenAI API error: {e}"
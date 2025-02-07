import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = True  #  Для разработки
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')  # Обязательно задай!
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

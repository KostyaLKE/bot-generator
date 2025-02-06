import os
from dotenv import load_dotenv

load_dotenv()

class Config:  # <- Класс Config с большой буквы
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    STABILITY_API_KEY = os.environ.get('STABILITY_API_KEY')
    # ... другие настройки
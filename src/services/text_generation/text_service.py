# bot-generator-main/src/services/text_generation/text_service.py
from src.services.text_generation import openai_service  # Импортируем openai_service
from src.config import Config
import openai

class TextService:
    def __init__(self):
        self.openai_api_key = Config.OPENAI_API_KEY
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not set in environment variables")
        openai.api_key = self.openai_api_key

    def get_prompt_for_social_network(self, network_name, news_text):
        """Возвращает промпт для заданной социальной сети."""

        if network_name.lower() == "instagram":
            return f"""
Ты — профессиональный SMM-копирайтер, который создает увлекательные посты для Instagram.
Твоя задача — написать пост на основе следующей новости:
"{news_text}"

📌 Правила оформления:
- Максимальная длина поста: 150 символов
- Стиль: динамичный, яркий, с эмоциями
- Используй эмодзи, чтобы привлечь внимание
- Добавь призыв к действию (например, "Что думаете? Делитесь в комментариях! 💬")
- В конце добавь до 5 популярных хештегов, связанных с темой

🎯 Твой результат должен быть кратким, увлекательным и соответствовать стилистике Instagram!
"""
        elif network_name.lower() == "twitter" or network_name.lower() == "x":
            return f"""
Ты — эксперт по контенту для Twitter (X).
Напиши цепляющий твит на основе следующей новости:
"{news_text}"

📌 Правила:
- Длина: до 200 символов
- Минимум "воды", только суть!
- Можно добавить интригу или вопрос
- Не используй сложные конструкции
- В конце добавь 2-3 хештега

🎯 Твой текст должен быть емким, но мощным!
"""
        elif network_name.lower() == "facebook":
            return f"""
Ты — профессиональный копирайтер, который пишет посты для Facebook.
На основе следующей новости создай вовлекающий пост:
"{news_text}"

📌 Правила:
- Длина: 200-500 символов
- Формат: 2-3 абзаца, без сложных фраз
- Добавь призыв к обсуждению
- В конце — 3-4 хештега

🎯 Твой текст должен быть интересным и удобным для чтения!
"""
        elif network_name.lower() == "tiktok":
            return f"""
Ты — креативный контент-мейкер TikTok.
Создай описание к видео на основе этой новости:
"{news_text}"

📌 Формат:
- Максимум 150 символов
- Минимум "воды", максимум вовлечения
- Добавь 4-5 популярных хештегов

🎯 Должно выглядеть так, будто это трендовый контент TikTok!
"""
        elif network_name.lower() == "telegram":
            return f"""
Ты — профессиональный Telegram-копирайтер.
Напиши лаконичный, но информативный пост по этой новости:
"{news_text}"

📌 Условия:
- Длина: 200-400 символов
- Не слишком официально, но и не "жёлтая пресса"
- Важные факты + легкий намек на вывод
- 2-3 хештега в конце

🎯 Текст должен быть полезным и читабельным!
"""
        else:  # Обработка "Другой" соцсети
            return f"""
Напиши пост для социальной сети {network_name} на основе следующего текста:

{news_text}

Постарайся сделать текст интересным и вовлекающим. Добавь несколько релевантных хэштегов.
"""


    def generate_text_for_social_media(self, news_text, social_networks, other_name):
        """
        Генерирует текст для разных социальных сетей на основе новостного текста.
        """

        try:
            results = {}
            for network in social_networks:
                if network == "other" and other_name:
                    network_name = other_name
                else:
                    network_name = network

                prompt = self.get_prompt_for_social_network(network_name, news_text)

                try:
                    response = openai.Completion.create(
                        engine="gpt-3.5-turbo-instruct", #  Используем gpt-3.5-turbo-instruct
                        prompt=prompt,
                        max_tokens=250,
                        n=1,
                        stop=None,
                        temperature=0.7,
                    )
                    generated_text = response.choices[0].text.strip()
                    results[network_name] = generated_text

                except openai.error.OpenAIError as e:
                    print(f"OpenAI API error: {e}")
                    results[network_name] = f"Ошибка при генерации текста для {network_name}: {e}"
                except Exception as e:
                    print(f"Unexpected error during text generation: {e}")
                    results[network_name] = f"Непредвиденная ошибка при генерации текста для {network_name}: {e}"


            return results

        except Exception as e:
            print(f"Error in TextService: {e}")
            raise


text_service = TextService()
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

    def generate_text_for_social_media(self, news_text, social_networks, other_name):
        """
        Генерирует текст для разных социальных сетей на основе новостного текста.

        Args:
            news_text: Исходный текст новости.
            social_networks: Список выбранных социальных сетей.
            other_name: Название другой социальной сети (если выбрано "Другое").

        Returns:
            Словарь с текстами для каждой социальной сети.
        """

        try:
            results = {}
            for network in social_networks:
                if network == "other" and other_name:
                    network_name = other_name
                else:
                    network_name = network

                # ---  ПРОСТЕЙШАЯ ЗАГЛУШКА для начала ---
                # prompt = f"Сгенерируй пост для {network_name} на основе текста: {news_text}"
                # response = openai.Completion.create(
                #   engine="text-davinci-003",  # Или другая модель
                #   prompt=prompt,
                #   max_tokens=150, # Можешь настроить
                #   n=1,
                #   stop=None,
                #   temperature=0.7, # Можешь настроить
                # )
                # generated_text = response.choices[0].text.strip()
                # results[network_name] = generated_text

                # ---  ВРЕМЕННАЯ ЗАГЛУШКА, ЧТОБЫ УБЕДИТЬСЯ, ЧТО ВСЁ РАБОТАЕТ ---
                results[network_name] = f"Заглушка текста для {network_name} на основе: {news_text}"


            return results

        except Exception as e:
            print(f"Error in TextService: {e}")
            raise  # Перебрасываем исключение, чтобы обработать его в контроллере


text_service = TextService()  # Создаем экземпляр сервиса
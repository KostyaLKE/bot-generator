import openai
import requests
from PIL import Image
from io import BytesIO
import os
from flask import Flask, request, render_template, url_for, send_from_directory
import logging

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_news_summary(news_text, api_key):
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты журналист. Переформулируй новость, сделав её краткой, но информативной."},
                {"role": "user", "content": news_text}
            ]
        )
        return response.choices[0].message.content.strip()
    except openai.OpenAIError as e:  # Более специфичное исключение
        logger.error(f"OpenAI API error (summary): {e}")
        return "Ошибка при генерации сводки новости. Пожалуйста, проверьте ваш API ключ и подключение к интернету."
    except Exception as e:
        logger.error(f"Unexpected error (summary): {e}")
        return "Произошла непредвиденная ошибка при генерации сводки."


def generate_detailed_prompt(news_text, api_key):
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты эксперт по визуализации. Преобразуй новость в детальное описание сцены для DALL·E. Описывай объект, стиль, освещение и детали."},
                {"role": "user", "content": news_text}
            ]
        )
        return response.choices[0].message.content.strip()
    except openai.OpenAIError as e:
        logger.error(f"OpenAI API error (prompt): {e}")
        return "Ошибка при генерации промпта для изображения. Пожалуйста, проверьте ваш API ключ."
    except Exception as e:
        logger.error(f"Unexpected error (prompt): {e}")
        return "Произошла непредвиденная ошибка при генерации промпта."


def generate_news_image(news_text, api_key, filename="news_image.png"):
    try:
        detailed_prompt = generate_detailed_prompt(news_text, api_key)
        if "Ошибка" in detailed_prompt: #Если произошла ошибка на предыдущем шаге
             return None, detailed_prompt
        
        client = openai.OpenAI(api_key=api_key)
        response = client.images.generate(
            model="dall-e-3",
            prompt=detailed_prompt,
            n=1,
            size="1024x1024"
        )

        image_url = response.data[0].url
        image_data = requests.get(image_url).content
        image = Image.open(BytesIO(image_data))

        # Создаем уникальное имя файла, чтобы избежать конфликтов
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)
        return image_path, None # Возвращаем путь и сообщение об ошибке (None если все хорошо)

    except openai.OpenAIError as e:
        logger.error(f"OpenAI API error (image): {e}")
        return None, "Ошибка при генерации изображения. Пожалуйста, проверьте ваш API ключ."
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error (image): {e}")
        return None, "Ошибка при загрузке изображения. Проверьте подключение к интернету."
    except Exception as e:
        logger.error(f"Unexpected error (image): {e}")
        return None, "Произошла непредвиденная ошибка при генерации изображения."



@app.route('/', methods=['GET', 'POST'])
def index():
    news_text = None
    image_path = None
    uploaded_image = None
    error_message = None  # Добавляем переменную для хранения сообщений об ошибках

    if request.method == 'POST':
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            error_message = "Ошибка: API ключ OpenAI не найден.  Установите переменную окружения OPENAI_API_KEY."
            logger.error(error_message)
            return render_template('index.html', error_message=error_message), 500

        news_text_input = request.form['news_text']
        uploaded_file = request.files['image']

        if uploaded_file.filename != '':
            # Генерируем уникальное имя файла
            filename = os.path.basename(uploaded_file.filename)
            uploaded_image = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(uploaded_image)
            # Для корректного отображения в HTML, используем url_for
            uploaded_image = url_for('static', filename=f'uploads/{filename}')


        news_text = generate_news_summary(news_text_input, api_key)
        if "Ошибка" in news_text: #Если произошла ошибка на предыдущем шаге
            error_message = news_text
            news_text = None
    
        # Генерация изображения (используем сокращенный текст)
        if news_text:  # Только если текст новости успешно сгенерирован
          generated_image_path, generation_error = generate_news_image(news_text, api_key)
          if generated_image_path:
              image_path = url_for('static', filename=f'uploads/{os.path.basename(generated_image_path)}')
          elif generation_error:  # Если произошла ошибка генерации
             error_message = generation_error


        return render_template('index.html', news_text=news_text, image_path=image_path, uploaded_image=uploaded_image, error_message=error_message)

    return render_template('index.html', news_text=news_text, image_path=image_path, uploaded_image=uploaded_image, error_message=error_message)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000, debug=True)  # debug=True для вывода ошибок в браузер (ТОЛЬКО для разработки!)
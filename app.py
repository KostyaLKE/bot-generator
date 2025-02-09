import openai
import requests
from PIL import Image
from io import BytesIO
import os
from flask import Flask, request, render_template

app = Flask(__name__)

def generate_news_summary(news_text, api_key):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Ты журналист. Переформулируй новость, сделав её краткой, но информативной."},
            {"role": "user", "content": news_text}
        ]
    )
    return response["choices"][0]["message"]["content"].strip()

def generate_news_image(news_text, api_key, output_path="static/news_image.png"):
    openai.api_key = api_key
    response = openai.Image.create(
        model="dall-e-3",
        prompt=news_text,
        n=1,
        size="1024x1024"
    )
    
    image_url = response["data"][0]["url"]
    image_data = requests.get(image_url).content
    image = Image.open(BytesIO(image_data))
    image.save(output_path)
    return output_path

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        api_key = os.getenv("OPENAI_API_KEY")
        news_text = request.form['news_text']
        new_text = generate_news_summary(news_text, api_key)
        image_path = generate_news_image(new_text, api_key)
        return render_template('index.html', news_text=new_text, image_path=image_path)
    return render_template('index.html', news_text=None, image_path=None)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
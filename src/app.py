from flask import Flask, jsonify
from src.services.text_generation.simple_test import test_openai
from src.config import Config

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/api/test')
def test_route():
    result = test_openai()
    return jsonify({"result": result})

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])

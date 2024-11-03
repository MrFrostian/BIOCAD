from flask import Flask, request, jsonify
import requests
import json

# Создание приложения Flask
app = Flask(__name__)
APP_AUTH_TOKEN = 'b5721c78-875d-4608-a482-72a6bc62122b'

# Функция для отправки запроса в Yandex GPT
def request_yandex_gpt(api_token, text_part, question):
    URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    data = {
        "modelUri": "gpt://b1gt14ubklm3vfrp1hpe/yandexgpt/rc",
        "completionOptions": {"temperature": 0.35, "maxTokens": 2000},
        "messages": [
            {"role": "system", "text": "Ты — эксперт в анализе научной литературы."},
            {"role": "user", "text": f"Текст статьи (часть): {text_part}"},
            {"role": "user", "text": f"Вопрос: {question}"}
        ]
    }
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_token}"
    }
    response = requests.post(URL, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['result']['alternatives'][0]['message']['text']
    return None

# Эндпоинт для обработки вопросов и отправки их в Yandex GPT
@app.route('/askQuestion', methods=['POST'])
def ask_question():
    # Получаем вопрос и apiToken из запроса
    question = request.json.get('question')
    auth_header = request.headers.get('Authorization')
    if auth_header:
        api_token = auth_header.split(" ")[1]  # Извлекаем токен из заголовка Authorization
    else:
        return jsonify({"error": "Authorization header missing"}), 400

    if not question or not api_token:
        return jsonify({"error": "Invalid question or token"}), 400

    # Здесь можно вставить текст статьи или часть текста напрямую
    text_part = "Здесь ваш текст статьи или часть текста, если он разбит на части"  # Замените на ваш текст

    # Отправляем запрос в Yandex GPT
    answer = request_yandex_gpt(api_token, text_part, question)
    if answer:
        return jsonify({"answer": answer})
    return jsonify({"error": "No answer found"}), 404

if __name__ == '__main__':
    app.run(debug=False, port=5000, host='176.214.202.28')
    
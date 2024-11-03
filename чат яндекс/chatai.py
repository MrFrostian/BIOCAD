import requests
import json
import datetime
import jwt  # pip install pyjwt
import PyPDF2  # pip install PyPDF2

# Загрузка информации из key.json
with open("authorized_key.json") as f:
    service_account_info = json.load(f)

service_account_id = service_account_info['service_account_id']
key_id = service_account_info['id']
private_key = service_account_info['private_key']

now = datetime.datetime.now(datetime.timezone.utc)
payload = {
    'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
    'iss': service_account_id,
    'iat': int(now.timestamp()),
    'exp': int((now + datetime.timedelta(minutes=10)).timestamp())
}
encoded_jwt = jwt.encode(payload, private_key, algorithm='PS256', headers={'kid': key_id})

# Получение IAM-токена
url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
headers = {"Content-Type": "application/json"}
data = {"jwt": encoded_jwt}

response = requests.post(url, headers=headers, json=data)
iam_token = response.json().get("iamToken")

if iam_token:
    print("IAM-токен успешно получен.")
    #print(iam_token)
else:
    print("Ошибка получения токена:", response.json())
    exit()


# Функция для разбивки текста на части с учетом ограничения на количество токенов
def split_text(text, max_tokens=8000):
    words = text.split()
    parts = []
    part = []
    token_count = 0

    for word in words:
        # Предполагаем, что в среднем одно слово составляет 1.5 токена
        token_count += 1.5
        part.append(word)
        if token_count >= max_tokens:
            parts.append(" ".join(part))
            part = []
            token_count = 0

    if part:
        parts.append(" ".join(part))

    return parts


# Функция для отправки запроса в Yandex GPT для ответа на вопросы по тексту
def request_yandex_gpt(iam_token, text_part, question):
    URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    data = {
        "modelUri": "gpt://b1gt14ubklm3vfrp1hpe/yandexgpt/rc",
        "completionOptions": {"temperature": 0.35, "maxTokens": 2000},
        "messages": [
            {"role": "system",
             "text": "Ты — эксперт в анализе научной литературы. Пользователь задает вопросы по загруженному тексту, и ты отвечаешь на них подробно и точно."},
            {"role": "user", "text": f"Текст статьи (часть): {text_part}"},
            {"role": "user", "text": f"Вопрос: {question}"}
        ]
    }

    # Отправка запроса
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {iam_token}"
    }
    response = requests.post(URL, headers=headers, json=data)

    # Обработка ответа
    if response.status_code == 200:
        result_text = response.json()['result']['alternatives'][0]['message']['text']
        print("Ответ от Yandex GPT:")
        return result_text
    else:
        print("")
        return None


# Функция для чтения текста из PDF файла
def read_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text() + "\n"
    return text


# Чтение текста из файла 1.pdf
pdf_file_path = '1.pdf'  # Укажите путь к вашему PDF файлу
user_text = read_pdf(pdf_file_path)

# Разделение текста на части
text_parts = split_text(user_text)

# Бесконечный цикл для взаимодействия с пользователем
while True:
    question = input("Задайте вопрос по загруженному тексту (или введите 'exit' для завершения): ")
    if question.lower() == 'exit':
        print("Чат завершен.")
        break

    # Проходимся по каждой части текста, пока не получим ответ
    for part in text_parts:
        answer = request_yandex_gpt(iam_token, part, question)
        if answer:
            print("Ответ:", answer)
            break  # Останавливаемся на первом полученном ответе
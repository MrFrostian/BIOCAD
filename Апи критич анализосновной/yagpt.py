import requests
import json
import datetime
import jwt  # pip install pyjwt
import PyPDF2  # pip install PyPDF2

# Загрузка информации из key.json
with open("key.json") as f:
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


# Улучшенный промпт критического анализа для каждой части текста
def get_analysis_prompt(part_number, total_parts):
    return f"""Ты — эксперт в анализе научной литературы, выполняющий работу точно и профессионально.
Проведи критический анализ части {part_number} из {total_parts} научной статьи, охватывая следующие аспекты:
1. **Название**
2. **Новизна и актуальность исследования**
3. **Цель и задачи исследования**
4. **Структура статьи**
5. **Методологические аспекты**
6. **Теоретические и практические аспекты**
7. **Обоснованность выводов и заключений**
8. **Заключение**
9. **Ссылки, упомянутые в этой части**
10. **Рекомендации по дальнейшему чтению**
11. **Определения из текста**

Если информация неполная или отсутствует, отметь это. Пожалуйста, следуй этому плану для анализа каждой части."""


# Функция для отправки запроса в Yandex GPT для анализа части текста
def request_yandex_gpt(iam_token, text_part, part_number, total_parts):
    URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    prompt = get_analysis_prompt(part_number, total_parts)
    data = {
        "modelUri": "gpt://b1gt14ubklm3vfrp1hpe/yandexgpt/rc",
        "completionOptions": {"temperature": 0.35, "maxTokens": 2000},
        "messages": [
            {"role": "system", "text": prompt},
            {"role": "user", "text": text_part}
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
        print(f"Ответ от Yandex GPT для части {part_number} из {total_parts}:")
        print(result_text)
        return result_text
    else:
        print(f"Ошибка: {response.status_code}, {response.text}")
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

# Цикл для обработки каждой части текста и получения критического анализа
all_results = []
for i, part in enumerate(text_parts, start=1):
    result = request_yandex_gpt(iam_token, part, i, len(text_parts))
    if result:
        all_results.append(f"Часть {i} из {len(text_parts)}:\n{result}\n")

# Объединение и вывод всех результатов
final_analysis = "\n".join(all_results)
print("Полный анализ статьи:")
print(final_analysis)
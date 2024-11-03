import streamlit as st
import fitz  # PyMuPDF
import requests
import json
import uuid
import base64
import urllib3

urllib3.disable_warnings()

client_id = ('3d95a105-f766-4007-b237-47ca37f32c5d')
secret = ('a37fea8e-bc9a-40ab-8c74-5ec9bb9c306a')
auth = ('M2Q5NWExMDUtZjc2Ni00MDA3LWIyMzctNDdjYTM3ZjMyYzVkOmEzN2ZlYThlLWJjOWEtNDBhYi04Yzc0LTVlYzliYjljMzA2YQ==')

# Получение base64-encoded credentials (если необходимо)
credentials = f"{client_id}:{secret}"
encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
# Проверяем, совпадают ли закодированные креденшелы с предоставленными
# encoded_credentials == auth

def get_token(auth_token, scope='GIGACHAT_API_PERS'):
    # Создаем идентификатор UUID (36 знаков)
    rq_uid = str(uuid.uuid4())

    # API URL
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    # Заголовки
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': rq_uid,
        'Authorization': f'Basic {auth_token}'
    }

    # Тело запроса
    payload = {
        'scope': scope
    }

    try:
        # Делаем POST запрос с отключенной SSL верификацией
        response = requests.post(url, headers=headers, data=payload, verify=False)
        return response
    except requests.RequestException as e:
        print(f"Ошибка: {str(e)}")
        return -1

def get_chat_completion(auth_token, user_message, system_prompt=None):
    """
    Выполняет запрос к GigaChat API для получения ответа на заданное сообщение.

    Параметры:
    - auth_token (str): токен авторизации.
    - user_message (str): сообщение пользователя.
    - system_prompt (str): системный промпт (необязательно).

    Возвращает:
    - Ответ API в формате JSON.
    """
    # URL API, к которому мы обращаемся
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    # Подготовка сообщений
    messages = []

    # Если есть системный промпт, добавляем его в сообщения
    if system_prompt:
        messages.append({
            "role": "assistant",
            "content": system_prompt
        })

    # Добавляем сообщение пользователя
    messages.append({
        "role": "user",
        "content": user_message
    })

    # Подготовка данных запроса в формате JSON
    payload = json.dumps({
        "model": "GigaChat",
        "messages": messages,
        "temperature": 1.2,
        "top_p": 0.3,
        "n": 1,
        "stream": False,
        "max_tokens": 1500,
        "repetition_penalty": 1,
        "update_interval": 0
    })

    # Заголовки запроса
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {auth_token}'
    }

    # Выполнение POST-запроса и возвращение ответа
    try:
        response = requests.post(url, headers=headers, data=payload, verify=False)
        if response.status_code != 200:
            print(f"Статус код: {response.status_code}")
            print(f"Ответ API: {response.text}")
            return None
        return response.json()
    except requests.RequestException as e:
        print(f"Произошла ошибка: {str(e)}")
        return None


def main():
    # Настройка темы и заголовка приложения
    st.set_page_config(page_title="GigaChat PDF Summarizer", layout="wide")

    # Определение цветов
    primary_color = "#FF00FF"
    secondary_color = "#00FFFF"
    accent_color = "#000080"

    # Заголовок с кастомным стилем
    st.markdown(
        f"""
        <style>
        .title {{
            font-size: 40px;
            color: {primary_color};
            text-align: center;
            margin-bottom: 20px;
        }}
        .file-uploader {{
            border: 2px dashed {primary_color};
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            background-color: {secondary_color};
            color: {accent_color};
        }}
        .text-area {{
            background-color: {secondary_color};
            color: {accent_color};
        }}
        </style>
        """,
        


        unsafe_allow_html=True
    )

    st.markdown('<div class="title">GigaChat PDF Summarizer</div>', unsafe_allow_html=True)

    # Создаем область для загрузки файла
    uploaded_file = st.file_uploader("Выберите PDF файл", type="pdf", label_visibility="collapsed")

    if uploaded_file is not None:
        # Открываем PDF-файл из загруженного файла
        pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")

        # Инициализируем переменную content для хранения текста
        content = ""
        for page in pdf_document:
            content += page.get_text()

        pdf_document.close()
        st.session_state['pdf_text'] = content  # Сохраняем текст в сессии

        # Выводим текст PDF
        st.subheader("Содержимое PDF:")
        st.text_area("Текст из PDF:", value=content, height=300, key="text_area", 
                      help="Текст из загруженного PDF", 
                      label_visibility="collapsed", 
                      disabled=True)  # Делаем текстовое поле неактивным
    elif uploaded_file is None and 'pdf_text' in st.session_state:
        st.session_state['pdf_text'] = ""

if __name__ == "__main__":
    main()


if 'result_text' not in st.session_state:
    st.session_state['result_text'] = ""

# Обрабатываем текст при нажатии на кнопку "Сократить"
if st.button("Сократить") and 'pdf_text' in st.session_state:
    if st.session_state['pdf_text']:
        # Получаем токен для доступа к GigaChat API
        response = get_token(auth)
        if response != -1:
            giga_token = response.json()['access_token']

            # Формируем системный промпт
            system_prompt = (
                "Ты - эксперт-аналитик. Я - исследователь, который хочет получить краткий анализ "
                "прилагаемой научной статьи. Тщательно проанализируй прилагаемый документ и составь краткое содержание. "
                "Убедись, что в резюме отражены основные положения, ключевые аргументы, подтверждающие доказательства "
                "и выводы, сделанные автором. Сохрани исходный контекст и замысел, оставляя резюме кратким."
            )

            content = st.session_state['pdf_text']
            user_message = 'сделай краткий анализ данной научной статьи: ' + content

            # Получаем ответ от GigaChat
            answer_json = get_chat_completion(giga_token, user_message, system_prompt)

            if answer_json:
                try:
                    # Извлекаем ответ
                    answer = answer_json['choices'][0]['message']['content']
                    st.session_state['result_text'] = answer  # Сохраняем answer в сессии
                except (KeyError, IndexError) as e:
                    st.error(f"Ошибка при обработке ответа: {str(e)}")
                    st.error(f"Полный ответ API: {answer_json}")
            else:
                st.error("Не удалось получить ответ от API.")
        else:
            st.error("Не удалось получить токен авторизации.")
    else:
        st.warning("Пожалуйста, загрузите PDF файл.")

# Отображаем сокращенный текст и кнопки управления
col_abridged, col_buttons = st.columns(2)
with col_abridged:
    st.subheader("Сокращенный текст:")

with col_buttons:
    col_copy, col_clear = st.columns(2)


    with col_clear:
        if st.button("Очистить", use_container_width=True):
            st.session_state['result_text'] = ""

# Отображаем переменную answer в текстовом поле
st.text_area("Результат (answer):", value=st.session_state['result_text'], height=400)
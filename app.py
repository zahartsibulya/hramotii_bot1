import os
import wikipedia
import requests
import openai
from flask import Flask, request, jsonify

app = Flask(__name__)

# Перевірка змінних середовища
openai_api_key = os.getenv("OPENAI_API_KEY")
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

if not openai_api_key or not telegram_bot_token:
    raise ValueError("Необхідно встановити змінні середовища OPENAI_API_KEY та TELEGRAM_BOT_TOKEN.")

openai.api_key = openai_api_key
wikipedia.set_lang("uk")

# Отримання відповіді з Wikipedia
def get_answer_from_wikipedia(query):
    try:
        page = wikipedia.page(query)
        return page.summary[:1000]
    except wikipedia.exceptions.DisambiguationError as e:
        try:
            page = wikipedia.page(e.options[0])
            return page.summary[:1000]
        except:
            return "Запит неоднозначний. Будь ласка, уточніть питання."
    except wikipedia.exceptions.PageError:
        return "На жаль, не знайдено відповідної статті у Вікіпедії."
    except Exception as e:
        print(f"Помилка Wikipedia: {e}")
        return "Помилка при зверненні до Вікіпедії."

# Отримання відповіді з ChatGPT
def get_answer_from_chatgpt(query):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ти експерт з української мови."},
                {"role": "user", "content": query}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Помилка при зверненні до ChatGPT: {e}")
        return "На жаль, не вдалося отримати відповідь від ChatGPT."

# Надсилання повідомлення в Telegram
def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print(f"Помилка при надсиланні повідомлення в Telegram: {response.status_code}, {response.text}")

# Обробка запиту Dialogflow
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print(f"Отримано запит: {data}")

    try:
        query = data["queryResult"]["queryText"]
        intent = data["queryResult"]["intent"]["displayName"]
        chat_id = data["originalDetectIntentRequest"]["payload"]["data"]["message"]["chat"]["id"]

        print(f"Інтент: {intent} | Запит: {query}")

        if intent == "ChatGPT":
            answer = get_answer_from_chatgpt(query)
        else:
            answer = get_answer_from_wikipedia(query)

        send_telegram_message(chat_id, answer)

        return jsonify({"fulfillmentText": answer})
    except Exception as e:
        print(f"Помилка при обробці вебхуку: {e}")
        return jsonify({"fulfillmentText": "Сталася помилка при обробці запиту."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

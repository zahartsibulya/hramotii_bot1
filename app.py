from flask import Flask, request, jsonify
import openai
import wikipedia
import requests
import os

app = Flask(__name__)

# Налаштування API ключів
openai.api_key = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Wikipedia налаштування
wikipedia.set_lang("uk")

def get_answer_from_wikipedia(query):
    try:
        page = wikipedia.page(query)
        return page.summary[:1000]  # обмежимо довжину
    except wikipedia.exceptions.PageError:
        return None
    except wikipedia.exceptions.DisambiguationError as e:
        # Візьмемо перше запропоноване значення
        try:
            page = wikipedia.page(e.options[0])
            return page.summary[:1000]
        except:
            return None

def get_answer_from_chatgpt(query):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # або gpt-4, якщо маєте доступ
            messages=[
                {"role": "system", "content": "Ти експерт з української мови."},
                {"role": "user", "content": query}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return "На жаль, не вдалося отримати відповідь від ChatGPT."

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    
    try:
        query = data["queryResult"]["queryText"]
        chat_id = data["originalDetectIntentRequest"]["payload"]["data"]["message"]["chat"]["id"]
    except KeyError:
        return jsonify({"fulfillmentText": "Невідомий формат запиту."})

    # Пошук у Wikipedia
    wiki_answer = get_answer_from_wikipedia(query)
    
    if wiki_answer:
        answer = wiki_answer
    else:
        answer = get_answer_from_chatgpt(query)

    # Відправка у Telegram
    send_telegram_message(chat_id, answer)
    
    return jsonify({"fulfillmentText": answer})

if __name__ == "__main__":
    app.run(port=5000)

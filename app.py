from flask import Flask, request, jsonify
import openai
import wikipedia
import os

app = Flask(__name__)

# Налаштування API ключів
openai.api_key = os.getenv("OPENAI_API_KEY")

# Wikipedia налаштування
wikipedia.set_lang("uk")

def get_answer_from_wikipedia(query):
    try:
        page = wikipedia.page(query)
        return page.summary[:1000]  # обмежимо довжину
    except wikipedia.exceptions.PageError:
        return None
    except wikipedia.exceptions.DisambiguationError as e:
        try:
            page = wikipedia.page(e.options[0])
            return page.summary[:1000]
        except:
            return None

def get_answer_from_chatgpt(query):
    try:
        prompt = f"""
Ти — мовний експерт з української мови. Дай чітку, стислу і корисну відповідь на запит користувача.
Запит: {query} """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ти експерт з української мови. Відповідай грамотно, стисло, українською."},
                {"role": "user", "content": f"Проаналізуй запит українською мовою та дай точну відповідь:\n{query}"}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print("Помилка GPT:", e)
        return "На жаль, не вдалося отримати відповідь від ChatGPT."

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    try:
        query = data["queryResult"]["queryText"]
    except KeyError:
        return jsonify({"fulfillmentText": "Не вдалося розпізнати запит."})

    # Отримаємо відповідь з Вікіпедії або GPT
    answer = get_answer_from_wikipedia(query)
    if not answer:
        answer = get_answer_from_chatgpt(query)

    # Повертаємо відповідь назад до Dialogflow (і Telegram)
    return jsonify({"fulfillmentText": answer})

if __name__ == "__main__":
    app.run(port=5000)

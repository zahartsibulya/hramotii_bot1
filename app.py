from flask import Flask, request, jsonify
import openai
import wikipedia
import os

app = Flask(name)

# Налаштування API ключів
openai.api_key = os.getenv("My Test Key")

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
        client = openai.OpenAI()  # новий клієнт (OpenAI >= 1.0)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ти експерт з української мови. Відповідай чітко, грамотно і по суті."},
                {"role": "user", "content": query}
            ]
        )
        return response.choices[0].message.content
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

    print(f"Отримано запит: {query}")

    answer = get_answer_from_wikipedia(query)
    if not answer:
        answer = get_answer_from_chatgpt(query)

    print(f"Відповідь: {answer}")
    return jsonify({"fulfillmentText": answer})

if name == "main":
    app.run(port=5000)

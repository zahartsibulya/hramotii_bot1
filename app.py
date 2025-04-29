from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)  # <-- Це має бути до використання @app.route

# 🔐 GPT (опційно)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    user_query = req["queryResult"]["queryText"]

    # 1. Пошук у Wikipedia
    wiki_result = search_wikipedia(user_query)

    # 2. Якщо GPT доступний — сформулювати відповідь прямо з питання
    if OPENAI_API_KEY:
        if wiki_result:
            prompt = f"Українською мовою, коротко і чітко поясни: {wiki_result}"
        else:
            prompt = f"Українською мовою, коротко і грамотно відповідай на питання: {user_query}"
        gpt_answer = ask_gpt(prompt)
        result = gpt_answer or wiki_result or "Вибач, я не зміг знайти відповідь."
    else:
        result = wiki_result or "На жаль, я не знайшов точної відповіді."

    print("🔁 Відповідь:", result)  # для логів

    return jsonify({"fulfillmentText": result})

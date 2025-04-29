from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# 🔐 GPT (опційно)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def search_wikipedia(query):
    url = f"https://uk.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("extract")
    return None

def ask_gpt(prompt):
    if not OPENAI_API_KEY:
        return None
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    return None

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    user_query = req["queryResult"]["queryText"]

    # 1. Спроба знайти у Wikipedia
    wiki_result = search_wikipedia(user_query)

    # 2. Якщо GPT увімкнено, уточнити/переформулювати
    if wiki_result and OPENAI_API_KEY:
        refined_answer = ask_gpt(f"Сформулюй коротку й зрозумілу відповідь на українською: {wiki_result}")
        result = refined_answer or wiki_result
    else:
        result = wiki_result or "На жаль, я не знайшов точної відповіді."

    return jsonify({"fulfillmentText": result})
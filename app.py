from flask import Flask, request, jsonify
import wikipedia
import re

app = Flask(__name__)

# Налаштування мови Вікіпедії
wikipedia.set_lang("uk")

def get_answer_from_wikipedia(query):
    try:
        print(f"[LOG] Пошук у Вікіпедії: '{query}'")
        page = wikipedia.page(query)
        summary = page.summary[:1000]
        print(f"[LOG] Знайдено сторінку: {page.title}")
        return summary
    except wikipedia.exceptions.PageError:
        print("[LOG] Сторінку не знайдено (PageError)")
        return None
    except wikipedia.exceptions.DisambiguationError as e:
        print(f"[LOG] Дизамбігуація, спроба взяти перший варіант: {e.options[0]}")
        try:
            page = wikipedia.page(e.options[0])
            return page.summary[:1000]
        except:
            return None
    except Exception as e:
        print(f"[ERROR] {e}")
        return None

def search_fallback(query):
    # Пробуємо пошукати за ключовими словами, якщо основний пошук не спрацював
    words = re.findall(r'\b\w{4,}\b', query)  # тільки слова довші за 3 літери
    print(f"[LOG] Резервний пошук: {words}")
    for word in words:
        result = get_answer_from_wikipedia(word)
        if result:
            return result
    return None

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    try:
        query = data["queryResult"]["queryText"]
    except KeyError:
        return jsonify({"fulfillmentText": "Не вдалося розпізнати запит."})

    print(f"[REQUEST] Отримано запит: '{query}'")

    # Пошук у Вікіпедії
    answer = get_answer_from_wikipedia(query)
    if not answer:
        answer = search_fallback(query)
    if not answer:
        answer = "На жаль, я не знайшов інформації у Вікіпедії."

    print(f"[RESPONSE] Відповідь: {answer[:100]}...\n")

    return jsonify({"fulfillmentText": answer})

if __name__ == "__main__":
    app.run(port=5000)

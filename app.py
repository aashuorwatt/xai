from flask import Flask, request, jsonify
import requests
import re
import os

app = Flask(__name__)

# ✅ Secure: API key from Railway ENV
API_KEY = os.getenv("DEEPSEEK_API_KEY")

if not API_KEY:
    raise ValueError("API key not found. Set DEEPSEEK_API_KEY in Railway variables.")

def clean_text(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)

def ask_ai(prompt):
    url = "https://api.deepseek.com/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are Vasudev, a wise, friendly and helpful AI assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)

        if response.status_code != 200:
            return f"API Error ({response.status_code}): {response.text[:300]}"

        result = response.json()

        if "choices" not in result or not result["choices"]:
            return f"Empty response: {str(result)[:300]}"

        reply = result["choices"][0]["message"]["content"]
        return clean_text(reply)

    except requests.exceptions.RequestException as e:
        return f"Connection Error: {str(e)}"
    except Exception as e:
        return f"Unexpected Error: {str(e)}"


@app.route('/')
def home():
    return "Vasudev AI Server Running 🚀"


@app.route('/ask')
def ask():
    user_msg = request.args.get('msg')

    if not user_msg:
        return jsonify({"error": "No message provided"}), 400

    reply = ask_ai(user_msg)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

from flask import Flask, request, jsonify
import requests
import os
import re

app = Flask(__name__)

# 🔐 Secure API Key (Railway ENV)
API_KEY = os.getenv("DEEPSEEK_API_KEY")

if not API_KEY:
    raise ValueError("❌ Missing API Key. Set DEEPSEEK_API_KEY in Railway.")

# 🧹 Clean & format text
def format_response(text):
    # Remove weird/unicode chars
    text = re.sub(r'[^\x00-\x7F]+', '', text)

    # Remove extra spaces/newlines
    text = re.sub(r'\s+', ' ', text).strip()

    # Optional: Limit length (avoid spammy replies)
    return text[:1000]

# 🤖 AI Request Function
def ask_ai(prompt):
    url = "https://api.deepseek.com/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": "You are Vasudev, a calm, wise and helpful AI. Reply in short, clear and clean format."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.6,
        "max_tokens": 500
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=30)

        if res.status_code != 200:
            return f"⚠️ API Error {res.status_code}"

        data = res.json()

        if not data.get("choices"):
            return "⚠️ Empty AI response"

        reply = data["choices"][0]["message"]["content"]

        return format_response(reply)

    except requests.exceptions.Timeout:
        return "⏱️ Request timeout. Try again."
    except requests.exceptions.ConnectionError:
        return "🌐 Connection error."
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# 🏠 Home Route
@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "name": "Vasudev AI",
        "message": "Server running successfully 🚀"
    })

# 💬 Ask Route
@app.route("/ask", methods=["GET"])
def ask():
    user_msg = request.args.get("msg")

    if not user_msg:
        return jsonify({
            "status": "error",
            "message": "No message provided"
        }), 400

    reply = ask_ai(user_msg)

    return jsonify({
        "status": "success",
        "question": user_msg,
        "reply": reply
    })

# 🚀 Run Server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

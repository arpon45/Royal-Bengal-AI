from flask import Flask, request, jsonify, render_template, Response
import os
import json
from flask_limiter import Limiter
from openai import OpenAI
from collections import defaultdict

app = Flask(__name__)

# ✅ Load API key from environment
API_KEY = os.getenv("OPENROUTER_API_KEY")
print("✅ API_KEY Loaded:", "YES" if API_KEY else "NO")


# ✅ Initialize OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
    default_headers={
        "HTTP-Referer": "https://your-render-url.onrender.com",  # Replace with your real Render URL
        "X-Title": "Royal Bengal AI",
    }
)

# ✅ Limiter and usage tracker
limiter = Limiter(app=app, key_func=lambda: request.remote_addr)
usage_stats = defaultdict(lambda: {'count': 0, 'last_used': 0})

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
@limiter.limit("10/minute")
def chat():
    try:
        data = request.json
        messages = data.get('messages', [])
        
        if not isinstance(messages, list) or not messages:
            return jsonify({"error": "Invalid message format"}), 400

        for msg in messages:
            if 'role' not in msg or 'content' not in msg or not msg['content'].strip():
                return jsonify({"error": "Invalid message structure"}), 400
            msg['content'] = msg['content'].strip()[:2000]

        completion = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct",  # or "openai/gpt-3.5-turbo" if needed
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
            stream=False
        )
        
        return jsonify({"response": completion.choices[0].message.content})

    except Exception as e:
        return jsonify({"error": f"AI service error: {str(e)}"}), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"error": f"Rate limit exceeded: {e.description}"}), 429

@app.errorhandler(500)
def internal_error_handler(e):
    return jsonify({"error": "Something went wrong. Try again later."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os
from flask_cors import CORS

app = Flask(__name__)
# Increase maximum content length to 10MB
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB limit
CORS(app)

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
    timeout=30
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        if not data or 'messages' not in data:
            return jsonify({"error": "Invalid request format"}), 400

        try:
            response = client.chat.completions.create(
                extra_headers={
                    "Authorization": f"Bearer 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",
                    "HTTP-Referer": "http://localhost:5000",
                    "X-Title": "Royal Bengal AI",
                    "Content-Type": "application/json"
                },
                model="anthropic/claude-3-haiku",
                messages=data['messages'],
                temperature=0.7,
                max_tokens=1000,
                top_p=0.9,
                frequency_penalty=0.2,
                presence_penalty=0.2
            )
            
            return jsonify({
                "response": response.choices[0].message.content
            })
            
        except Exception as api_error:
            print(f"API Error: {str(api_error)}")
            return jsonify({
                "error": "Service temporarily unavailable",
                "solution": "Please refresh the page and try again",
                "status": "retry"
            }), 503

    except Exception as e:
        print(f"Server Error: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
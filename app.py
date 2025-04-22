from flask import Flask, request, jsonify, render_template, Response
from openai import OpenAI
import json
from flask_limiter import Limiter
import time
from collections import defaultdict

app = Flask(__name__)

API_KEY = "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"
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
    default_headers={
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "Royal Bengal AI",
    }
)

# Initialize rate limiter
limiter = Limiter(app=app, key_func=lambda: request.remote_addr)

# Initialize usage tracking
usage_stats = defaultdict(lambda: {'count': 0, 'last_used': 0})

@app.route('/')
def home():
    return render_template('index.html')

@app.before_request
def validate_request():
    if request.method == 'POST' and request.path == '/chat':
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        data = request.get_json()
        if not data.get('messages'):
            return jsonify({"error": "Missing messages in request"}), 400

@app.route('/chat', methods=['POST'])
@limiter.limit("10/minute")
def chat():
    try:
        data = request.json
        messages = data.get('messages', [])
        
        if not isinstance(messages, list) or len(messages) == 0:
            return jsonify({"error": "Invalid message format"}), 400
            
        for msg in messages:
            if 'role' not in msg or 'content' not in msg:
                return jsonify({"error": "Invalid message structure"}), 400
            if not isinstance(msg['content'], str) or len(msg['content'].strip()) == 0:
                return jsonify({"error": "Message content must be a non-empty string"}), 400

        for msg in messages:
            msg['content'] = msg['content'].strip()[:2000]
        
        completion = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct",
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
            stream=data.get('stream', False)
        )
        
        if data.get('stream', False):
            def generate():
                try:
                    for chunk in completion:
                        if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            if content.strip():
                                yield f"data: {json.dumps({'content': content})}\n\n"
                except Exception as e:
                    error_detail = str(e)
                    print(f"Streaming error: {error_detail}")
                    yield f"data: {json.dumps({'error': error_detail})}\n\n"
            return Response(generate(), mimetype='text/event-stream')
        else:
            try:
                ai_response = completion.choices[0].message.content
                if not ai_response:
                    raise ValueError("Empty response from AI")
                return jsonify({"response": ai_response})
            except Exception as e:
                error_detail = str(e)
                print(f"Response error: {error_detail}")
                return jsonify({"error": error_detail}), 500
        
    except Exception as e:
        error_detail = str(e)
        print(f"Chat error: {error_detail}")
        return jsonify({"error": error_detail}), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "error": f"Rate limit exceeded: {e.description}"
    }), 429

@app.errorhandler(500)
def internal_error_handler(e):
    return jsonify({
        "error": "Server encountered an unexpected error. Developers have been notified."
    }), 500

if __name__ == '__main__':
    # Remove explicit dotenv loading since API_KEY is already defined
    import os
    os.environ["FLASK_SKIP_DOTENV"] = "1"
    
    app.run(debug=True, port=5000)
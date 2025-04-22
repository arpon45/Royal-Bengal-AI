from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")  # Matches .env value
)

# Create a chat completion
completion = client.chat.completions.create(
    extra_headers={
        "HTTP-Referer": "<YOUR_SITE_URL>",  # Optional. Replace with your site URL
        "X-Title": "<YOUR_SITE_NAME>",      # Optional. Replace with your site name
    },
    extra_body={},
    model="deepseek/deepseek-r1:free",
    messages=[
        {
            "role": "user",
            "content": "What is the meaning of life?"
        }
    ]
)

# Print the response
print(completion.choices[0].message.content)
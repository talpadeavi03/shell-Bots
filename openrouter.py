import requests
import json

# Set your OpenRouter API key here
API_KEY = "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"  # Replace with your actual API key

# OpenRouter API endpoint
url = "https://openrouter.ai/api/v1/chat/completions"

# Chat loop
while True:
    prompt = input("You: ")
    if prompt.lower() in ["exit", "quit"]:
        print("Goodbye!")
        break

    # Define payload with correct model name
    payload = {
        "model": "deepseek/deepseek-chat",  # Correct model for OpenRouter
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 150
    }

    # Set headers
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Send POST request
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # Check response status
    if response.status_code == 200:
        result = response.json()
        # Extract plain text content
        plain_text_response = result['choices'][0]['message']['content'].strip()
        print(plain_text_response)
    else:
        print(f"Error: {response.status_code}, {response.text}")


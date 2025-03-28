import requests
import json

# Set your OpenRouter API key here
API_KEY = "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"  # Replace with your actual API key

# OpenRouter API endpoint
url = "https://openrouter.ai/api/v1/chat/completions"

# Initialize conversation history
conversation_history = []

# Chat loop
while True:
    prompt = input("You: ")
    if prompt.lower() in ["exit", "quit"]:
        print("Goodbye!")
        break

    # Add user message to conversation history
    conversation_history.append({"role": "user", "content": prompt})

    # Define payload with full conversation history
    payload = {
        "model": "deepseek/deepseek-chat",  # Correct model name
        "messages": conversation_history,   # Send full conversation history
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
        # Extract plain text response
        plain_text_response = result['choices'][0]['message']['content'].strip()
        print(f"DeepSeek: {plain_text_response}")
        
        # Add assistant's response to conversation history
        conversation_history.append({"role": "assistant", "content": plain_text_response})
    else:
        print(f"Error: {response.status_code}, {response.text}")

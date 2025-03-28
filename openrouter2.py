import requests
import json
import os
import platform
import subprocess

# Set your OpenRouter API key here
API_KEY = "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"  # Replace with your actual API key

# OpenRouter API endpoint
url = "https://openrouter.ai/api/v1/chat/completions"

# Initialize conversation history
conversation_history = []

# Function to run system commands and return output
def run_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Error: {result.stderr.strip()}"
    except Exception as e:
        return f"Command execution failed: {str(e)}"

# Function to detect and execute commands
def check_and_execute(prompt):
    if prompt.lower() == "clear":
        os.system("clear" if platform.system() != "Windows" else "cls")
        return "Screen cleared! 😊"
    
    elif "ip address" in prompt.lower() or "show ip" in prompt.lower():
        # Run appropriate command based on OS
        command = "ip a" if platform.system() != "Windows" else "ipconfig"
        return run_command(command)
    
    elif "list files" in prompt.lower() or "show files" in prompt.lower():
        command = "ls" if platform.system() != "Windows" else "dir"
        return run_command(command)
    
    elif "current directory" in prompt.lower() or "pwd" in prompt.lower():
        return run_command("pwd" if platform.system() != "Windows" else "cd")

    else:
        return None

# Chat loop
while True:
    prompt = input("You: ")
    if prompt.lower() in ["exit", "quit"]:
        print("Goodbye! 👋")
        break

    # Check if it's a command
    command_output = check_and_execute(prompt)
    if command_output:
        print(command_output)
        continue

    # Add user message to conversation history
    conversation_history.append({"role": "user", "content": prompt})

    # Define payload with full conversation history
    payload = {
        "model": "deepseek/deepseek-chat",  # Correct model name
        "messages": conversation_history,
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

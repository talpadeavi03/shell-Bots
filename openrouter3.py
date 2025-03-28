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

# Function to detect and execute commands with fuzzy matching
def check_and_execute(prompt):
    prompt_lower = prompt.lower()

    # Clear the screen
    if any(keyword in prompt_lower for keyword in ["clear", "clean", "wipe screen"]):
        os.system("clear" if platform.system() != "Windows" else "cls")
        return "✅ Screen cleared!"

    # Show IP address
    elif any(keyword in prompt_lower for keyword in ["show ip", "ip address", "get ip"]):
        command = "ip a" if platform.system() != "Windows" else "ipconfig"
        return run_command(command)

    # List files or directories
    elif any(keyword in prompt_lower for keyword in ["list files", "show files", "directory contents"]):
        command = "ls" if platform.system() != "Windows" else "dir"
        return run_command(command)

    # Show current directory
    elif any(keyword in prompt_lower for keyword in ["current directory", "where am i", "pwd"]):
        command = "pwd" if platform.system() != "Windows" else "cd"
        return run_command(command)

    return None

# Chat loop
while True:
    prompt = input("You: ")
    if prompt.lower() in ["exit", "quit"]:
        print("Goodbye! 👋")
        break

    # Check if it's a terminal command
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

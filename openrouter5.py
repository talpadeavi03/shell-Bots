import openai
import subprocess
import json

# Set OpenRouter API key
API_KEY = "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"  # Replace with your actual API key
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# Recognized system commands with fuzzy matching
COMMAND_MAP = {
    "ls": "ls -lh",
    "show directory": "ls -lh",
    "list dir": "ls -lh",
    "display files": "ls -lh",
    "read directory": "ls -lh",
    "pwd": "pwd",
    "clear": "clear",
    "ip address": "ip addr",
    "disk usage": "df -h",
    "show ip": "ip addr",
    "check network": "ping -c 4 google.com",
    "show processes": "ps aux",
    "kill process": "kill -9 ",
    "system info": "uname -a",
    "memory usage": "free -m",
    "create directory": "mkdir new_directory",
    "delete directory": "rm -rf ",
    "show calendar": "cal",
    "disk space": "df -h",
    "change permissions": "chmod 755 ",
    "change owner": "chown ",
    "list running services": "service --status-all",
    "modify user": "usermod -aG sudo ",
    "add user": "useradd ",
    "check firewall": "ufw status",
    "top processes": "top",
    "update packages": "sudo yum update -y",
    "reboot system": "sudo reboot",
    "shutdown system": "sudo shutdown -h now",
}

# Run terminal commands
def run_command(command):
    try:
        output = subprocess.check_output(command, shell=True, text=True)
        return output
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"

# Check and execute command if available
def check_and_execute(prompt):
    prompt_lower = prompt.lower()

    # Fuzzy match to find the correct command
    for key, command in COMMAND_MAP.items():
        if key in prompt_lower:
            if "delete directory" in key or "kill process" in key or "change permissions" in key or "change owner" in key:
                arg = input(f"Specify the target for '{key}': ")
                command += arg
            return run_command(command)
    return None

# Save successfully executed commands for future learning
def save_command_history(command):
    with open("command_history.txt", "a") as file:
        file.write(f"{command}\n")

# Send request to OpenRouter API
def get_openrouter_response(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek/deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 100
    }

    response = subprocess.run(
        ["curl", "-X", "POST", BASE_URL, "-H", f"Authorization: Bearer {API_KEY}", "-H", "Content-Type: application/json", "-d", json.dumps(data)],
        capture_output=True,
        text=True
    )

    try:
        result = json.loads(response.stdout)
        if "choices" in result:
            return result["choices"][0]["message"]["content"].strip()
        else:
            return f"Error: {result.get('error', {}).get('message', 'Unknown error occurred.')}"
    except json.JSONDecodeError:
        return "Error decoding response from OpenRouter."

# Main chat loop
while True:
    prompt = input("You: ")
    
    # Exit on "quit" or "exit"
    if prompt.lower() in ["exit", "quit"]:
        print("Goodbye! 👋")
        break
    
    # Check and execute terminal command first
    command_output = check_and_execute(prompt)
    if command_output:
        print(command_output)
        save_command_history(prompt)  # Save successful command
        continue  # Skip AI if terminal command is executed
    
    # If no valid command, send prompt to OpenRouter
    ai_response = get_openrouter_response(prompt)
    print(f"DeepSeek: {ai_response}")

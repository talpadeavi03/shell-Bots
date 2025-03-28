import openai
import subprocess
import json
from fuzzywuzzy import fuzz, process

# Set OpenRouter API key
API_KEY = "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"  # Replace with your actual API key
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
COMMAND_MAP_FILE = "command_map.json"

print("🚀 Starting the chatbot...") 
# Load command map dynamically
def load_command_map():
    try:
        with open(COMMAND_MAP_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Save command map dynamically
def save_command_map(command_map):
    with open(COMMAND_MAP_FILE, "w") as file:
        json.dump(command_map, file, indent=4)

# Load existing commands
command_map = load_command_map()

# Run terminal commands
def run_command(command):
    try:
        output = subprocess.check_output(command, shell=True, text=True)
        return output.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"

# Ask user to teach unknown commands
def learn_new_command(user_input):
    print(f"🤔 I don't know how to execute '{user_input}'. Can you tell me the exact terminal command?")
    new_command = input("Enter the terminal command: ")
    
    if new_command.strip():
        command_map[user_input] = new_command.strip()
        save_command_map(command_map)
        print(f"✅ Learned how to handle '{user_input}'! Command saved for future use.")
    else:
        print("⚠️ Command not saved. Please try again next time.")

# Find the best matching command using fuzzy logic
def find_best_match(user_input):
    if not command_map:
        return None, 0
    best_match_data = process.extractOne(user_input, command_map.keys())
    if best_match_data is None:
        return None, 0
    best_match, score = best_match_data
    return best_match, score

# Check and execute command dynamically
def check_and_execute(user_input):
    # Check for a perfect match first
    if user_input in command_map:
        command = command_map[user_input]
        result = run_command(command)

import os
import subprocess
import json
import re
from fuzzywuzzy import process

# Set your OpenRouter API Key
API_KEY = "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"
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# Keywords to auto-detect and execute commands
EXECUTION_KEYWORDS = ["run", "execute", "start", "launch", "perform"]
CLEAR_SCREEN_KEYWORDS = ["clear", "wipe", "clean", "clear screen"]
ERROR_FIX_SUGGESTIONS = ["suggest", "correct", "fix", "resolve"]

# Predefined common commands for fuzzy matching
COMMON_COMMANDS = ["ls", "pwd", "whoami", "hostname", "clear", "cd", "rm", "cp", "mv", "mkdir", "rmdir", "cat"]

# Function to query OpenRouter API for AI response
def query_ai(user_input, purpose):
    try:
        data = {
            "model": "deepseek/deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are an AI assistant that converts natural language to Bash/Linux commands and helps with troubleshooting errors."},
                {"role": "user", "content": f"{purpose}: {user_input}"}
            ],
            "max_tokens": 150
        }

        response = subprocess.run(
            [
                "curl",
                "-X", "POST", BASE_URL,
                "-H", f"Authorization: Bearer {API_KEY}",
                "-H", "Content-Type: application/json",
                "-d", json.dumps(data)
            ],
            capture_output=True,
            text=True
        )

        result = json.loads(response.stdout)
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"].strip()
        else:
            error_msg = result.get("error", {}).get("message", "Unknown error occurred.")
            print(f"❌ Error: {error_msg}")
            return None

    except Exception as e:
        print(f"❌ Error connecting to OpenRouter API: {e}")
        return None

# Function to extract and clean valid commands from AI response
def extract_command(ai_response):
    command_match = re.search(r"```bash\n(.*?)```", ai_response, re.DOTALL)
    if command_match:
        return command_match.group(1).strip()

    lines = ai_response.splitlines()
    for line in lines:
        if line.strip() and not line.startswith("#"):
            return line.strip()

    return None

# Function to run Linux commands safely
def run_command(command):
    try:
        output = subprocess.check_output(command, shell=True, text=True)
        return output.strip()
    except subprocess.CalledProcessError as e:
        return f"⚠️ Error executing command: {e}\n💡 Suggestion: Double-check the command syntax or use 'sudo'."

# Detect intent: Command, Conversation, or Help
def detect_intent(user_input):
    if any(keyword in user_input.lower() for keyword in EXECUTION_KEYWORDS + COMMON_COMMANDS):
        return "run_command"
    elif any(keyword in user_input.lower() for keyword in ERROR_FIX_SUGGESTIONS):
        return "get_suggestion"
    else:
        return "ask_question"

# Correct mistyped commands using fuzzy matching
def correct_command(user_input):
    best_match, score = process.extractOne(user_input, COMMON_COMMANDS)
    if score > 80:
        return best_match
    return None

# Handle command errors and suggest corrections
def handle_error(command):
    suggestion_response = query_ai(command, "Suggest corrections for this command")
    if suggestion_response:
        print("💡 AI Suggestion(s):")
        suggestions = suggestion_response.split("\n")
        for idx, suggestion in enumerate(suggestions, start=1):
            print(f"{idx}. {suggestion}")
        return suggestions
    return None

# Main AI-powered shell with enhanced functionality
def ai_shell():
    print("🤖 AI-Powered Shell & Chatbot Ready! Type 'exit' to quit.")

    while True:
        user_input = input("AI Shell > ").strip()

        # Exit the shell
        if user_input in ["exit", "quit"]:
            print("👋 Goodbye! Exiting AI Shell.")
            break

        # Clear screen command
        if should_clear_screen(user_input):
            os.system("clear")
            print("✅ Screen cleared!")
            continue

        # Detect intent
        intent = detect_intent(user_input)

        if intent == "run_command":
            corrected_command = correct_command(user_input)
            if corrected_command:
                print(f"✅ Auto-corrected to '{corrected_command}'. Running...")
                user_input = corrected_command

            ai_response = query_ai(user_input, "Convert to Linux command")
            if ai_response:
                suggested_command = extract_command(ai_response)
                if suggested_command:
                    print(f"🔹 AI Generated Command: {suggested_command}")
                    result = run_command(suggested_command)
                    if "Error executing command" in result:
                        print(result)
                        handle_error(suggested_command)
                    else:
                        print(f"🔹 Command Output:\n{result}")
                else:
                    print("❌ No valid command found.")
            else:
                print("❌ AI response error. Try again.")

        elif intent == "get_suggestion":
            suggestions = handle_error(user_input)
            if not suggestions:
                print("❌ No suggestions available. Try again.")

        elif intent == "ask_question":
            ai_response = query_ai(user_input, "Respond conversationally")
            if ai_response:
                print(f"💬 AI: {ai_response}")
            else:
                print("❌ Unable to process conversation. Try again.")

# Run the AI shell
ai_shell()

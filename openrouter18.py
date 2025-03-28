import os
import subprocess
import json
import re

# Set your OpenRouter API Key
API_KEY = "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"
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# Keywords to detect if user wants to run a command explicitly
EXECUTION_KEYWORDS = ["run", "execute", "start", "launch", "perform"]
CLEAR_SCREEN_KEYWORDS = ["clear", "wipe", "clean", "clear screen"]

# Function to query OpenRouter AI for command conversion or conversation
def query_ai(user_input, purpose):
    try:
        # Define the request payload
        data = {
            "model": "deepseek/deepseek-chat",  # Using DeepSeek model from OpenRouter
            "messages": [
                {"role": "system", "content": "You are an AI assistant that ONLY returns valid Linux commands when asked to run or convert commands. If no command is needed, respond as a chatbot."},
                {"role": "user", "content": f"{purpose}: {user_input}"}
            ],
            "max_tokens": 150
        }

        # Send request to OpenRouter using curl
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

        # Parse the JSON response
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

# Updated extract_command function to filter and prioritize valid commands
def extract_command(ai_response):
    # Look for code blocks or single-line commands
    command_match = re.findall(r"```bash\n(.*?)```|```(.*?)```|^\s*([\w./-]+.*)$", ai_response, re.MULTILINE | re.DOTALL)

    valid_commands = []
    for match in command_match:
        # Extract command by removing unnecessary content
        command = match[0] or match[1] or match[2]
        if command and not command.lower().startswith(("to", "or", "press", "replace")):
            command = command.strip()

            # Check if it's a valid shell command to avoid running invalid suggestions
            if re.match(r"^[a-zA-Z0-9_./|><\"' -]+$", command):
                valid_commands.append(command)

    return valid_commands

# Improved run_command function to validate and execute commands safely
def run_command(command):
    try:
        # Validate the command syntax before running
        if not command or not re.match(r"^[a-zA-Z0-9_./|><\"' -]+$", command):
            return "⚠️ Invalid or potentially unsafe command. Skipping execution."

        # Execute the command safely
        output = subprocess.check_output(command, shell=True, text=True)
        return output.strip()
    except subprocess.CalledProcessError as e:
        # Detect and provide suggestions for command errors
        return f"⚠️ Error executing command: {e}\n💡 Suggestion: Double-check the command syntax or use 'sudo'."

# Check if user wants to execute a command explicitly
def should_auto_execute(user_input):
    for keyword in EXECUTION_KEYWORDS:
        if keyword in user_input.lower():
            return True
    return False

# Check if user wants to clear the screen explicitly
def should_clear_screen(user_input):
    for keyword in CLEAR_SCREEN_KEYWORDS:
        if keyword in user_input.lower():
            return True
    return False

# Main AI-powered hybrid shell and chatbot
def ai_shell():
    print("🤖 AI-Powered Shell & Chatbot Ready! Type 'exit' to quit.")
    
    while True:
        user_input = input("AI Shell > ").strip()

        # Exit the shell
        if user_input in ["exit", "quit"]:
            print("👋 Goodbye! Exiting AI Shell.")
            break

        # Check for clear screen request
        if should_clear_screen(user_input):
            os.system("clear")
            print("✅ Screen cleared!")
            continue

        # Check if the user wants to run a command explicitly
        if should_auto_execute(user_input) or any(keyword in user_input for keyword in ["list", "create", "delete", "show", "move", "copy", "install", "update", "remove", "search", "clear", "ip", "hostname", "username", "whoami", "usage"]):
            # Detect and convert to command
            ai_response = query_ai(user_input, "Convert this to a valid Linux shell command")

            if ai_response:
                suggested_commands = extract_command(ai_response)

                if suggested_commands:
                    # Run the first valid command found
                    for suggested_command in suggested_commands:
                        print(f"\n🔹 AI Generated Command: {suggested_command}")
                        # Auto-execute the first safe command
                        result = run_command(suggested_command)
                        if result:
                            print(f"🔹 Command Output:\n{result}")
                            break
                else:
                    print("❌ No valid command found in AI response. Try again.")
            else:
                print("❌ Could not generate a command. Try again.")
        
        # Handle general conversation or fallback to AI response
        else:
            ai_response = query_ai(user_input, "Answer this question or respond to the conversation")

            if ai_response:
                print(f"💬 AI: {ai_response}")
            else:
                print("❌ Unable to process the conversation. Try again.")

# Run the AI shell
ai_shell()

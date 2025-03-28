import os
import subprocess
import json
import re

# Set your OpenRouter API Key
API_KEY = "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"
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# Keywords for command execution
EXECUTION_KEYWORDS = ["run", "execute", "start", "launch", "perform"]
CLEAR_SCREEN_KEYWORDS = ["clear", "wipe", "clean", "clear screen"]

# Function to query OpenRouter AI for command conversion or conversation
def query_ai(user_input, purpose):
    try:
        # Define the request payload
        data = {
            "model": "deepseek/deepseek-chat",  # Using DeepSeek model from OpenRouter
            "messages": [
                {"role": "system", "content": "You are an AI that returns valid Linux commands when asked to execute or fix commands. Otherwise, respond as a chatbot."},
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

# Function to extract valid commands from AI response
def extract_command(ai_response):
    if not ai_response:
        return []

    # Extract commands inside code blocks or single-line commands
    command_match = re.findall(r"```bash\n(.*?)```|```(.*?)```|^\s*([\w./*\-]+.*)$", ai_response, re.MULTILINE | re.DOTALL)
    valid_commands = []

    for match in command_match:
        command = match[0] or match[1] or match[2]
        if command:
            command = command.strip()
            # Avoid invalid responses or explanations
            if not any(keyword in command.lower() for keyword in ["to", "or", "press", "replace", "alternatively", "here", "try", "suggest", "use"]):
                valid_commands.append(command)

    # Fallback: Detect single-line commands
    single_line_commands = re.findall(r"^\s*([\w./*\-]+(?:\s+[\w./*\-]+)*)", ai_response, re.MULTILINE)
    for cmd in single_line_commands:
        if cmd and not cmd.startswith(("To", "Or", "Use", "Replace", "Alternatively")):
            valid_commands.append(cmd.strip())

    return valid_commands

# Function to run Linux commands safely
def run_command(command):
    try:
        output = subprocess.check_output(command, shell=True, text=True)
        return output.strip()
    except subprocess.CalledProcessError as e:
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

        # Detect if user explicitly wants to run a command
        if should_auto_execute(user_input) or any(keyword in user_input for keyword in ["list", "create", "delete", "show", "move", "copy", "install", "update", "remove", "search", "clear", "ip", "hostname", "username", "whoami", "cpu", "disk", "usage", "status", "storage"]):
            # Ask AI to convert to command
            ai_response = query_ai(user_input, "Convert this to a valid Linux shell command")

            if ai_response:
                suggested_commands = extract_command(ai_response)

                if suggested_commands:
                    for suggested_command in suggested_commands:
                        print(f"\n🔹 AI Generated Command: {suggested_command}")
                        # Automatically execute the command
                        result = run_command(suggested_command)
                        print(f"🔹 Command Output:\n{result}")
                        break  # Only execute the first valid command found
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

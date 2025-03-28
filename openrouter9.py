import os
import subprocess
import json

# Set your OpenRouter API Key
API_KEY = "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"  # Replace with your actual API key
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# Keywords to detect if user wants to "run" the command automatically
EXECUTION_KEYWORDS = ["run", "execute", "start", "launch", "perform"]

# Function to query OpenRouter AI for command conversion or conversation
def query_ai(user_input, purpose):
    try:
        # Define the request payload
        data = {
            "model": "deepseek/deepseek-chat",  # Using DeepSeek model from OpenRouter
            "messages": [
                {"role": "system", "content": "You are an AI assistant that can answer questions and convert natural language into valid Linux commands."},
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

# Function to run Linux commands
def run_command(command):
    try:
        output = subprocess.check_output(command, shell=True, text=True)
        return output.strip()
    except subprocess.CalledProcessError as e:
        return f"⚠️ Error executing command: {e}"

# Check if user wants to execute a command explicitly
def should_auto_execute(user_input):
    for keyword in EXECUTION_KEYWORDS:
        if keyword in user_input.lower():
            return True
    return False

# Main AI-powered hybrid shell and chatbot
def ai_shell():
    print("🤖 AI-Powered Shell & Chatbot Ready! Type 'exit' to quit.")
    
    while True:
        user_input = input("AI Shell > ").strip().lower()

        # Exit the shell
        if user_input in ["exit", "quit"]:
            print("👋 Goodbye! Exiting AI Shell.")
            break
        elif user_input in ["clear", "clear screen"]:
            os.system("clear")
            continue

        # Check if the user wants to run a command explicitly
        if should_auto_execute(user_input):
            # Detect and convert to command
            suggested_command = query_ai(user_input, "Convert this to a valid Linux shell command")
            
            if suggested_command:
                print(f"\n🔹 AI Generated Command: {suggested_command}")
                # Auto-execute the command without asking for confirmation
                result = run_command(suggested_command)
                print(f"🔹 Command Output:\n{result}")
            else:
                print("❌ Could not generate a command. Try again.")
        
        # Check if it's a Linux command-like request
        elif any(keyword in user_input for keyword in ["list", "create", "delete", "show", "run", "move", "copy", "install", "update", "remove", "search"]):
            # Step 1: Convert natural language to Linux command
            suggested_command = query_ai(user_input, "Convert this to a valid Linux shell command")
            
            if suggested_command:
                print(f"\n🔹 AI Generated Command: {suggested_command}")
                confirm = input("Run this command? (Yes/No) ").strip().lower()
                if confirm == "yes":
                    result = run_command(suggested_command)
                    print(f"🔹 Command Output:\n{result}")
                else:
                    print("🔹 Command not executed.")
            else:
                print("❌ Could not generate a command. Try again.")
        
        # Step 2: If not a command, chat with AI for general conversation
        else:
            ai_response = query_ai(user_input, "Answer this question or respond to the conversation")
            if ai_response:
                print(f"💬 AI: {ai_response}")
            else:
                print("❌ Unable to process the conversation. Try again.")

# Run the AI shell
ai_shell()

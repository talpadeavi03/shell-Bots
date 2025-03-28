import os
import subprocess
import json

# Set your OpenRouter API Key
API_KEY = "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"  # Replace with your actual API key
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# Function to query AI for command correction or conversion
def query_ai(user_input, purpose):
    try:
        # Define the request payload
        data = {
            "model": "deepseek/deepseek-chat",  # Using DeepSeek model from OpenRouter
            "messages": [
                {"role": "system", "content": "You are an AI assistant that converts natural language to Bash/Linux commands and fixes user mistakes."},
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

# Main function for AI-powered shell
def ai_shell():
    print("🔹 AI-Powered Linux Shell Assistant Started! Type 'exit' to quit.")
    
    while True:
        user_input = input("AI Shell > ").strip().lower()

        if user_input in ["exit", "quit"]:
            print("Exiting AI Assistant. 👋")
            break
        elif user_input in ["clear", "clear screen"]:
            os.system("clear")
            continue

        # Step 1: Detect Mistyped Commands
        corrected_command = query_ai(user_input, "Check for typos or errors and suggest a fix")
        if corrected_command and corrected_command != user_input:
            print(f"\n🔹 AI Suggestion: Did you mean '{corrected_command}'?")
            confirm = input("Run corrected command? (Yes/No) ").strip().lower()
            if confirm == "yes":
                user_input = corrected_command
            else:
                print("🔹 Running your original input.")

        # Step 2: Convert Natural Language to Linux Command
        suggested_command = query_ai(user_input, "Convert this to a valid Linux shell command")
        if suggested_command:
            print(f"\n🔹 AI Generated Command: {suggested_command}")
            confirm = input("Run this command? (Yes/No) ").strip().lower()
            if confirm == "yes":
                os.system(suggested_command)
            else:
                print("🔹 Command not executed.")
        else:
            print("❌ Could not generate a command. Try again.")

# Run the AI shell
ai_shell()

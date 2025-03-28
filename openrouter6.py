import os
import openai

# Set your OpenRouter API Key
API_KEY = "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"  # Replace with your actual API key
openai.api_key = API_KEY

# Function to query AI for command correction or conversion
def query_ai(user_input, purpose):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI assistant that converts natural language to Bash/Linux commands and fixes user mistakes."},
                {"role": "user", "content": f"{purpose}: {user_input}"}
            ],
            max_tokens=150
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Error connecting to AI API: {e}")
        return None

# Main function for AI-powered shell
def ai_shell():
    print("🔹 AI-Powered Linux Shell Assistant Started! Type 'exit' to quit.")
    
    while True:
        user_input = input("AI Shell > ").strip().lower()

        if user_input in ["exit", "quit"]:
            print("Exiting AI Assistant.")
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

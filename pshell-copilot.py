# Hybrid_PowerShell_AI_Assistant.py
import json
import subprocess
import hashlib
import requests
from datetime import datetime
from sentence_transformers import SentenceTransformer
import numpy as np

# ===== CONFIGURATION =====
COMMAND_DB = "hybrid_ps_commands.json"
BLOCKED_KEYWORDS = {
    "Remove-Item", "Invoke-Expression", "Format-Volume", ">", "|", 
    "net user", "reg delete", "Stop-Computer", "Restart-Computer",
    ";", "&&", "$(", "..\\", "`", "Start-Process", "New-PSDrive"
}

# Microsoft Copilot API (Free Tier)
COPILOT_API_URL = "https://api.copilot.microsoft.com/v1/chat/completions"
COPILOT_API_KEY = ""  # Leave empty for offline mode

# ===== SECURE HYBRID CORE =====
class HybridPowerShellAI:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.init_secure_db()
        self.online_mode = self.check_copilot_availability()
    
    def check_copilot_availability(self):
        """Verify if Copilot API is accessible"""
        if not COPILOT_API_KEY:
            return False
        try:
            test_prompt = {"messages": [{"role": "user", "content": "test"}]}
            response = requests.post(
                COPILOT_API_URL,
                headers={"Authorization": f"Bearer {COPILOT_API_KEY}"},
                json=test_prompt,
                timeout=3
            )
            return response.status_code == 200
        except:
            return False
    
    def get_copilot_suggestion(self, user_input: str):
        """Get AI suggestion from Copilot API with security filtering"""
        prompt = f"""
        You are a PowerShell expert. Respond with ONLY a command for: {user_input}
        Rules:
        1. Never use: {", ".join(BLOCKED_KEYWORDS)}
        2. Format as: 'Command: <command>'
        3. If unsafe, say: 'I cannot help with that request'
        """
        try:
            response = requests.post(
                COPILOT_API_URL,
                headers={"Authorization": f"Bearer {COPILOT_API_KEY}"},
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 100
                },
                timeout=5
            )
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                if "Command:" in content:
                    return content.split("Command:")[1].strip()
        except:
            pass
        return None
    
    def get_suggestion(self, user_input: str):
        """Hybrid suggestion system"""
        # First try local secure database
        local_cmd = self.find_similar_command(user_input)
        if local_cmd and self.is_command_safe(local_cmd):
            return local_cmd
        
        # If online available and no local match, try Copilot
        if self.online_mode:
            copilot_cmd = self.get_copilot_suggestion(user_input)
            if copilot_cmd and self.is_command_safe(copilot_cmd):
                return copilot_cmd
        
        # Fallback to local LLM if configured
        return self.handle_complex_query(user_input)

# ===== MAIN EXECUTION =====
if __name__ == "__main__":
    assistant = HybridPowerShellAI()
    mode = "ONLINE" if assistant.online_mode else "OFFLINE"
    print(f"🔒 Secure PowerShell AI Assistant ({mode} MODE)")
    print("Type '..' for suggestions, '?' for complex queries\n")
    
    while True:
        try:
            user_input = input("\nPS> ").strip()
            
            if user_input.lower() in ["exit", "quit"]:
                break
                
            # Auto-complete
            if user_input.endswith(".."):
                suggestions = assistant.realtime_autocomplete(user_input[:-2])
                print(f"🔍 Suggestions: {', '.join(suggestions)}")
                continue
                
            # Get command suggestion
            command = assistant.get_suggestion(user_input)
            print(f"\n💡 Suggested: {command}")
            
            confirm = input("✅ Execute? (y/n) > ").lower()
            if confirm == "y":
                assistant.execute_secure_command(command, user_input)
                
        except Exception as e:
            print(f"⚠️ Error: {e}")

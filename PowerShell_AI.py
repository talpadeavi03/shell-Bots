# PowerShell_AI_Assistant.py
import json
import subprocess
from datetime import datetime
from sentence_transformers import SentenceTransformer
import numpy as np

# ===== CONFIGURATION =====
COMMAND_DB = "ps_commands.json"
BLOCKED_KEYWORDS = {
    "Remove-Item", "Format-Volume", "Invoke-Expression",
    "Set-ExecutionPolicy", ">", "|", "net user", "reg delete",
    "Stop-Computer", "Restart-Computer", "Format-Volume"
}

DEFAULT_COMMANDS = [
    {"description": "List processes", "command": "Get-Process"},
    {"description": "List services", "command": "Get-Service"},
    {"description": "List files", "command": "Get-ChildItem"},
    {"description": "System info", "command": "systeminfo"}
]

# ===== CORE FUNCTIONALITY =====
class PowerShellAI:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.init_db()
    
    def init_db(self):
        """Initialize command database with defaults if empty"""
        try:
            with open(COMMAND_DB, "r") as f:
                if not json.load(f).get("commands"):
                    raise FileNotFoundError
        except (FileNotFoundError, json.JSONDecodeError):
            with open(COMMAND_DB, "w") as f:
                json.dump({"commands": DEFAULT_COMMANDS}, f, indent=2)
    
    def update_db(self, description: str, command: str):
        """Record new commands or increment usage count"""
        with open(COMMAND_DB, "r+") as f:
            db = json.load(f)
            for entry in db["commands"]:
                if entry["command"] == command:
                    entry["count"] = entry.get("count", 0) + 1
                    entry["last_used"] = datetime.now().strftime("%Y-%m-%d")
                    break
            else:
                db["commands"].append({
                    "description": description,
                    "command": command,
                    "count": 1,
                    "last_used": datetime.now().strftime("%Y-%m-%d")
                })
            f.seek(0)
            json.dump(db, f, indent=2)
    
    def is_command_safe(self, command: str) -> bool:
        """Block dangerous PowerShell operations"""
        cmd_lower = command.lower()
        return not any(
            kw.lower() in cmd_lower 
            for kw in BLOCKED_KEYWORDS
        ) and not any(
            # Block common injection patterns
            pattern in cmd_lower
            for pattern in ["&&", ";", "$(", "`", "..\\"]
        )
    
    def get_suggestion(self, user_input: str) -> str:
        """Find most relevant command using semantic search"""
        with open(COMMAND_DB) as f:
            db = json.load(f)
        
        # Encode all command descriptions
        descriptions = [cmd["description"] for cmd in db["commands"]]
        desc_embeddings = self.model.encode(descriptions)
        
        # Find best match
        input_embedding = self.model.encode(user_input)
        similarities = np.dot(desc_embeddings, input_embedding)
        best_match = db["commands"][np.argmax(similarities)]
        return best_match["command"]
    
    def run(self):
        """Main interaction loop"""
        print("🔹 PowerShell AI Assistant (Ctrl+C to exit)")
        print("Type 'history' to see your frequent commands\n")
        
        while True:
            user_input = input("\n💡 What do you want to do? > ").strip()
            
            if user_input.lower() == "history":
                self.show_history()
                continue
                
            command = self.get_suggestion(user_input)
            print(f"\n🔹 Suggested Command: {command}")
            
            confirm = input("✅ Run it? (y/n/edit) > ").lower()
            if confirm == "y":
                if not self.is_command_safe(command):
                    print("❌ Blocked potentially dangerous command!")
                    continue
                try:
                    subprocess.run(
                        ["powershell", "-Command", command], 
                        check=True,
                        shell=False  # Safer than shell=True
                    )
                    self.update_db(user_input, command)
                except Exception as e:
                    print(f"❌ Error: {e}")
            elif confirm == "edit":
                new_cmd = input("Enter corrected command: ")
                if self.is_command_safe(new_cmd):
                    self.update_db(user_input, new_cmd)
                    print("✅ Command saved for future!")
    
    def show_history(self):
        """Display frequently used commands"""
        with open(COMMAND_DB) as f:
            db = json.load(f)
        
        print("\n🕒 Your Frequently Used Commands:")
        for cmd in sorted(
            db["commands"], 
            key=lambda x: x.get("count", 0), 
            reverse=True
        )[:10]:  # Show top 10
            print(f"{cmd['command']: <30} ({cmd.get('count', 0)} uses)")

# ===== RUN THE ASSISTANT =====
if __name__ == "__main__":
    assistant = PowerShellAI()
    try:
        assistant.run()
    except KeyboardInterrupt:
        print("\n👋 Exiting PowerShell AI Assistant")

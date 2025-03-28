import requests
import json
import os
import platform
import subprocess

# Set your OpenRouter API key here
API_KEY = "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"  # Replace with your actual API key

# OpenRouter API endpoint
url = "https://openrouter.ai/api/v1/chat/completions"

# Initialize conversation history
conversation_history = []

# Function to run system commands and return output
def run_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Error: {result.stderr.strip()}"
    except Exception as e:
        return f"Command execution failed: {str(e)}"

# Function to detect and execute commands with fuzzy matching
def check_and_execute(prompt):
    prompt_lower = prompt.lower()

    ### --- Clear Screen ---
    if any(keyword in prompt_lower for keyword in ["clear", "clean", "wipe screen"]):
        os.system("clear" if platform.system() != "Windows" else "cls")
        return "✅ Screen cleared!"

    ### --- File & Directory Operations ---
    if any(keyword in prompt_lower for keyword in ["list files", "show files", "directory contents", "read directory", "ls"]):
        return run_command("ls -lh")

    elif "pwd" in prompt_lower or "current directory" in prompt_lower:
        return run_command("pwd")

    elif "change directory" in prompt_lower or "cd " in prompt_lower:
        path = prompt_lower.replace("change directory", "").replace("cd", "").strip()
        if path:
            try:
                os.chdir(path)
                return f"✅ Changed directory to {os.getcwd()}"
            except FileNotFoundError:
                return f"❗ Directory not found: {path}"
        else:
            return "❗ Please specify a directory to navigate."

    elif "create directory" in prompt_lower or "mkdir" in prompt_lower:
        dir_name = prompt_lower.replace("create directory", "").replace("mkdir", "").strip()
        if dir_name:
            return run_command(f"mkdir {dir_name}")
        else:
            return "❗ Please specify a directory name."

    elif "move file" in prompt_lower or "mv" in prompt_lower:
        args = prompt_lower.replace("move file", "").replace("mv", "").strip()
        return run_command(f"mv {args}")

    elif "copy file" in prompt_lower or "cp" in prompt_lower:
        args = prompt_lower.replace("copy file", "").replace("cp", "").strip()
        return run_command(f"cp {args}")

    elif "delete" in prompt_lower or "remove" in prompt_lower or "rm" in prompt_lower:
        target = prompt_lower.replace("delete", "").replace("remove", "").replace("rm", "").strip()
        if target:
            return run_command(f"rm -rf {target}")
        else:
            return "❗ Please specify the file or directory to delete."

    elif "create file" in prompt_lower or "touch" in prompt_lower:
        file_name = prompt_lower.replace("create file", "").replace("touch", "").strip()
        return run_command(f"touch {file_name}")

    ### --- File & Disk Utilities ---
    elif "show file" in prompt_lower or "read file" in prompt_lower or "cat" in prompt_lower:
        file_name = prompt_lower.replace("show file", "").replace("read file", "").replace("cat", "").strip()
        return run_command(f"cat {file_name}")

    elif "disk usage" in prompt_lower or "df" in prompt_lower:
        return run_command("df -h")

    elif "memory usage" in prompt_lower or "free" in prompt_lower:
        return run_command("free -m")

    elif "compress file" in prompt_lower or "tar" in prompt_lower:
        args = prompt_lower.replace("compress file", "").replace("tar", "").strip()
        return run_command(f"tar {args}")

    elif "zip" in prompt_lower:
        args = prompt_lower.replace("zip", "").strip()
        return run_command(f"zip {args}")

    elif "unzip" in prompt_lower:
        args = prompt_lower.replace("unzip", "").strip()
        return run_command(f"unzip {args}")

    ### --- User Management ---
    elif "whoami" in prompt_lower or "current user" in prompt_lower:
        return run_command("whoami")

    elif "show user id" in prompt_lower or "id" in prompt_lower:
        return run_command("id")

    elif "add user" in prompt_lower or "useradd" in prompt_lower:
        args = prompt_lower.replace("add user", "").replace("useradd", "").strip()
        return run_command(f"useradd {args}")

    elif "modify user" in prompt_lower or "usermod" in prompt_lower:
        args = prompt_lower.replace("modify user", "").replace("usermod", "").strip()
        return run_command(f"usermod {args}")

    elif "set password" in prompt_lower or "passwd" in prompt_lower:
        args = prompt_lower.replace("set password", "").replace("passwd", "").strip()
        return run_command(f"passwd {args}")

    ### --- Network & Security ---
    elif "ping" in prompt_lower:
        target = prompt_lower.replace("ping", "").strip()
        return run_command(f"ping -c 4 {target}")

    elif "show ip" in prompt_lower or "ip address" in prompt_lower:
        return run_command("ip a")

    elif "traceroute" in prompt_lower:
        target = prompt_lower.replace("traceroute", "").strip()
        return run_command(f"traceroute {target}")

    elif "firewall" in prompt_lower or "ufw" in prompt_lower:
        args = prompt_lower.replace("firewall", "").replace("ufw", "").strip()
        return run_command(f"ufw {args}")

    elif "iptables" in prompt_lower:
        args = prompt_lower.replace("iptables", "").strip()
        return run_command(f"iptables {args}")

    ### --- System Information & Process Management ---
    elif "system info" in prompt_lower or "uname" in prompt_lower:
        return run_command("uname -a")

    elif "list processes" in prompt_lower or "ps" in prompt_lower:
        return run_command("ps aux")

    elif "kill process" in prompt_lower or "kill" in prompt_lower:
        args = prompt_lower.replace("kill process", "").replace("kill", "").strip()
        return run_command(f"kill {args}")

    elif "show top processes" in prompt_lower or "top" in prompt_lower:
        return run_command("top -b -n 1")

    ### --- Package Management ---
    elif any(keyword in prompt_lower for keyword in ["install package", "apt", "yum", "pacman", "rpm"]):
        args = prompt_lower.replace("install package", "").strip()
        if "apt" in prompt_lower:
            return run_command(f"sudo apt install {args}")
        elif "yum" in prompt_lower:
            return run_command(f"sudo yum install {args}")
        elif "pacman" in prompt_lower:
            return run_command(f"sudo pacman -S {args}")
        elif "rpm" in prompt_lower:
            return run_command(f"sudo rpm -ivh {args}")
        else:
            return "❗ Please specify a package manager (apt, yum, pacman, rpm)."

    ### --- Miscellaneous ---
    elif "show calendar" in prompt_lower or "cal" in prompt_lower:
        return run_command("cal")

    elif "create alias" in prompt_lower or "alias" in prompt_lower:
        args = prompt_lower.replace("create alias", "").replace("alias", "").strip()
        return run_command(f"alias {args}")

    elif "find command location" in prompt_lower or "whereis" in prompt_lower:
        cmd_name = prompt_lower.replace("find command location", "").replace("whereis", "").strip()
        return run_command(f"whereis {cmd_name}")

    elif "what is" in prompt_lower or "whatis" in prompt_lower:
        cmd_name = prompt_lower.replace("what is", "").replace("whatis", "").strip()
        return run_command(f"whatis {cmd_name}")

    return None


# Chat loop
while True:
    prompt = input("You: ")
    if prompt.lower() in ["exit", "quit"]:
        print("Goodbye! 👋")
        break

    # Check if it's a terminal command
    command_output = check_and_execute(prompt)
    if command_output:
        print(command_output)
        continue

    # Add user message to conversation history
    conversation_history.append({"role": "user", "content": prompt})

    # Define payload with full conversation history
    payload = {
        "model": "deepseek/deepseek-chat",
        "messages": conversation_history,
        "max_tokens": 150
    }

    # Set headers
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Send POST request
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # Check response status
    if response.status_code == 200:
        result = response.json()
        # Extract plain text response
        plain_text_response = result['choices'][0]['message']['content'].strip()
        print(f"DeepSeek: {plain_text_response}")
        
        # Add assistant's response to conversation history
        conversation_history.append({"role": "assistant", "content": plain_text_response})
    else:
        print(f"Error: {response.status_code}, {response.text}")

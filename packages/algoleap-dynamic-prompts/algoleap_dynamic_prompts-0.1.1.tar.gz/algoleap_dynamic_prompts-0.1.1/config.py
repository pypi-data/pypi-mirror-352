import os
import json

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".llm_feedback_config.json")
PROMPT_PATH = os.path.join(os.path.expanduser("~"), ".llm_feedback_prompt.txt")

def save_api_key(api_key: str):
    config = {"api_key": api_key.strip()}
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f)

def load_api_key():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f).get("api_key", "")
    return ""

def save_system_prompt(prompt: str):
    with open(PROMPT_PATH, "w", encoding="utf-8") as f:
        f.write(prompt.strip())

def load_system_prompt():
    if os.path.exists(PROMPT_PATH):
        with open(PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read()
    return "You are a helpful assistant using the given file as reference."

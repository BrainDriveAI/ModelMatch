# src/api_clients.py
import os
from openai import OpenAI
import anthropic
import requests

# Debug: Print all env vars to confirm
print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))
print("ANTHROPIC_API_KEY:", os.getenv("ANTHROPIC_API_KEY"))
print("DEEPSEEK_API_KEY:", os.getenv("DEEPSEEK_API_KEY"))
print("OPENROUTER_API_KEY:", os.getenv("OPENROUTER_API_KEY"))

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
claude_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))  # Use Anthropic class
deepseek_client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)

def get_openrouter_models():
    try:
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        }
        response = requests.get("https://openrouter.ai/api/v1/models", headers=headers)
        response.raise_for_status()
        data = response.json()
        models = [m["id"] for m in data["data"] if m.get("id")]
        return sorted(set(models))
    except Exception as e:
        print(f"OpenRouter models fetch failed: {e}")
        return ["openai/gpt-4", "openai/gpt-3.5-turbo"]

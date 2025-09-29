# src/api_clients.py
import os
from openai import OpenAI
import anthropic
import requests

_openai_client = None
_claude_client = None


def get_openai_client() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY not set in environment.")
        _openai_client = OpenAI(api_key=key)
    return _openai_client


def get_claude_client() -> anthropic.Anthropic:
    global _claude_client
    if _claude_client is None:
        key = os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise ValueError("ANTHROPIC_API_KEY not set in environment.")
        _claude_client = anthropic.Anthropic(api_key=key)
    return _claude_client

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

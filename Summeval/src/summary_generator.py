# src/summary_generator.py

import requests
from src.api_clients import openai_client
import os

def generate_summary_from_openrouter(article, prompt, model):
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "X-Title": "BrainDrive Summary Gen",
        "HTTP-Referer": "http://localhost:7860"  # Added for local requests
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": f"{prompt}\n\n{article}"}
        ],
        "max_tokens": 1000
    }
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        print("OpenRouter Response Status:", res.status_code)  # Debug
        print("OpenRouter Response Body:", res.text)  # Debug
        res.raise_for_status()
        data = res.json()
        if 'choices' not in data:
            raise KeyError("'choices' key missing in response - likely API error (check printed response above)")
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error generating summary from OpenRouter: {str(e)}. Check terminal for response details and verify your API key/credits."

def is_prompt_valid_for_summary(prompt):
    check_prompt = f"You are a summarization prompt checker. Determine if the following prompt is strictly asking for a summary: '{prompt}'. Reply 'Yes' or 'No'."
    reply = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": check_prompt}],
        max_tokens=10
    ).choices[0].message.content.strip().lower()
    return "yes" in reply

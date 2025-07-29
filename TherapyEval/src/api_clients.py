import os
import anthropic
import openai
from openai import OpenAI
from anthropic import Anthropic

def init_clients():
    """Initialize API clients using environment variables."""
    try:
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")

        if not all([openai_key, anthropic_key, deepseek_key]):
            raise ValueError("Missing one or more API keys in environment variables.")

        openai_client = OpenAI(api_key=openai_key)
        anthropic_client = Anthropic(api_key=anthropic_key)
        deepseek_client = OpenAI(
            api_key=deepseek_key,
            base_url="https://api.deepseek.com/v1"
        )

        return openai_client, anthropic_client, deepseek_client

    except Exception as e:
        raise Exception(f"Failed to initialize API clients: {str(e)}")

def gpt4_mini_backend(system_msg, user_prompt, temperature):
    """Call GPT-4o Mini API."""
    openai_client, _, _ = init_clients()
    try:
        r = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature
        )
        return r.choices[0].message.content, r.usage.total_tokens
    except Exception as e:
        raise Exception(f"GPT-4o-mini error: {str(e)}")

def anthropic_backend(system_msg, user_prompt, temperature):
    """Call Anthropic Claude API."""
    _, anthropic_client, _ = init_clients()
    try:
        r = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            system=system_msg,
            messages=[{"role": "user", "content": user_prompt}],
            max_tokens=2000,
            temperature=temperature
        )
        text = r.content[0].text.strip()
        toks = r.usage.input_tokens + r.usage.output_tokens
        return text, toks
    except Exception as e:
        raise Exception(f"Anthropic error: {str(e)}")

def deepseek_backend(system_msg, user_prompt, temperature):
    """Call DeepSeek API."""
    _, _, deepseek_client = init_clients()
    try:
        r = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature
        )
        return r.choices[0].message.content, r.usage.total_tokens
    except Exception as e:
        raise Exception(f"DeepSeek error: {str(e)}")

# Register backends
BACKENDS = {
    "GPT-4o Mini": gpt4_mini_backend,
    "Claude 3.5 Sonnet": anthropic_backend,
    "DeepSeek Chat": deepseek_backend
}

from __future__ import annotations

import os
from typing import Optional, Tuple

from openai import OpenAI
from anthropic import Anthropic


_openai_client: Optional[OpenAI] = None
_anthropic_client: Optional[Anthropic] = None


def _get_openai_client() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY not set in environment.")
        _openai_client = OpenAI(api_key=key)
    return _openai_client


def _get_anthropic_client() -> Anthropic:
    global _anthropic_client
    if _anthropic_client is None:
        key = os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise ValueError("ANTHROPIC_API_KEY not set in environment.")
        _anthropic_client = Anthropic(api_key=key)
    return _anthropic_client


def gpt4_backend(system_msg: str, user_prompt: str, temperature: float) -> Tuple[str, int]:
    client = _get_openai_client()
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
    )
    usage = getattr(resp, "usage", None)
    total_tokens = getattr(usage, "total_tokens", None)
    if total_tokens is None:
        total_tokens = (getattr(usage, "prompt_tokens", 0) or 0) + (getattr(usage, "completion_tokens", 0) or 0)
    return resp.choices[0].message.content, int(total_tokens)


def claude_backend(system_msg: str, user_prompt: str, temperature: float) -> Tuple[str, int]:
    client = _get_anthropic_client()
    resp = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        system=system_msg,
        messages=[{"role": "user", "content": user_prompt}],
        max_tokens=4000,
        temperature=temperature,
    )
    text = resp.content[0].text.strip()
    usage = getattr(resp, "usage", None)
    total_tokens = (getattr(usage, "input_tokens", 0) or 0) + (getattr(usage, "output_tokens", 0) or 0)
    return text, int(total_tokens)


BACKENDS = {
    "GPT-4o": gpt4_backend,
    "Claude 3.5 Sonnet": claude_backend,
}

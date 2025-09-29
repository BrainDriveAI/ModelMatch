from __future__ import annotations

import json
from typing import Tuple

from .api_clients import gpt4_backend, claude_backend


def structure_conversation(conversation: str) -> str:
    turns = []
    for idx, line in enumerate(conversation.splitlines(), start=1):
        speaker, text = (line.split(":", 1) + [""])[:2]
        turns.append({"idx": idx, "speaker": speaker.strip(), "text": text.strip()})
    return json.dumps(turns, indent=2)


def call_judges(system_msg: str, user_prompt: str, temperature: float) -> Tuple[Tuple[str, int], Tuple[str, int]]:
    gpt4_result = gpt4_backend(system_msg, user_prompt, temperature)
    claude_result = claude_backend(system_msg, user_prompt, temperature)
    return gpt4_result, claude_result

import regex as re

WS = re.compile(r"\s+")
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")

def norm_text(s: str) -> str:
    return WS.sub(" ", (s or "").strip())

def word_count(s: str) -> int:
    if not s: return 0
    return len(re.findall(r"\b[\p{L}\p{N}’']+\b", s))

def sentences(s: str):
    s = norm_text(s)
    return SENT_SPLIT.split(s) if s else []

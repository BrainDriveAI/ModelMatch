import regex as re

# Actionability and clear asks grounded in research about explicit CTAs and timeliness.
ASK_PATTERNS = [
 r"(?i)\bplease (review|confirm|approve|advise|respond|sign|share)\b",
 r"(?i)\b(schedule|book|call|join|attend|register)\b",
 r"(?i)\b(action required|needs your approval|need your input)\b",
 r"(?i)\bby (mon|tue|wed|thu|fri|sat|sun|\d{1,2})(?:\s*(?:am|pm)?)?\b",
 r"(?i)^(please|review|confirm|approve|send|attach|reply|rsvp)\b",
 r"(?i)\b(could|can|would|please) (we|you) (move|change|reschedule|confirm|review|proceed)\b",
 r"(?i)\b(reschedule|move|change|follow up|following up)\b",
]

SUBJECT_USEFUL = [
 r"(?i)\breview\b", r"(?i)\bupdate\b", r"(?i)\binvoice\b", r"(?i)\bsummary\b", r"(?i)\bmetrics?\b",
 r"(?i)\bby (mon|tue|wed|thu|fri|\d{1,2})\b",
 r"(?i)\bschedul(?:e|ing)\b",
 r"(?i)\b(reminder|follow\s*up|deadline)\b",
]

GREETINGS = [r"(?i)^(hi|hello|hey|good (morning|afternoon|evening)|dear)\b"]
SIGNOFFS  = [r"(?i)\b(regards|best|sincerely|thanks|thank you|cheers)\b"]

# Patterns for tone analysis
PASSIVE_AGGRESSIVE = [
  r"(?i)per my last email",
  r"(?i)as previously (stated|mentioned)",
  r"(?i)as I (said|mentioned)",
  r"(?i)kindly (note|remind)",
  r"(?i)actually,?",
  r"(?i)you should have",
  r"(?i)if you had",
  r"(?i)hope that makes sense",
]

HOSTILE = [
  r"(?i)or else",
  r"(?i)you (will|shall) suffer",
  r"(?i)make sure you (guys\s+)?suffer",
  r"(?i)threat(en|s|ening)?",
  r"(?i)shut up",
]

# Spam-related regex groups grounded in industry guidance (urgency, rewards, marketing calls)
SPAM_URGENCY = [
  r"(?i)act now",
  r"(?i)limited time",
  r"(?i)expires in\b",
  r"(?i)24\s*hours",
  r"(?i)once in a lifetime",
  r"(?i)don['’]t miss out",
  r"(?i)urgent",
]

SPAM_REWARD = [
  r"(?i)congratulations",
  r"(?i)selected",
  r"(?i)exclusive (reward|deal|offer)?",
  r"(?i)reward",
  r"(?i)prize",
  r"(?i)cash",
  r"(?i)win(ner)?\b",
  r"(?i)\$\s*\d{2,}",
]

SPAM_CALLS = [
  r"(?i)click here",
  r"(?i)claim (your )?(prize|reward|offer)",
  r"(?i)redeem now",
]

SPAM_MARKETING = [
  r"(?i)free (trial|access|gift)",
  r"(?i)no obligation",
  r"(?i)risk[- ]?free",
]

HOMOPHONES = [
 ("its", "it's"), ("your","you're"), ("there","their"), ("there","they're"),
 ("to","too"), ("than","then"), ("affect","effect")
]

def any_match(patterns, text) -> bool:
    return any(re.search(p, text or "") for p in patterns)

def find_spans(patterns, text):
    spans=[]
    for p in patterns:
        for m in re.finditer(p, text or ""):
            spans.append((m.group(0), m.start(), m.end()))
    return spans
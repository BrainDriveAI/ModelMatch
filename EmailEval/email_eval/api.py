# email_eval/api.py — v2.3, with LLM-based clarity and grammar
# Six-metric evaluator for Subject + Body
# - Clarity: LLM-based
# - Length: hard-coded class-aware
# - Spam: LLM counts for SAFE marketing phrases + heuristics
# - Personalization: LLM cues + deterministic medium-best curve
# - Tone: LLM flags + deterministic math
# - Grammar: LLM-based

# Exports:
#   - evaluate(subject, body, engine="openai", weights=None) -> dict
#   - metric_keys() -> list[str]

from typing import Dict, Any, Tuple
import regex as re
import logging
from .config import DEFAULT_WEIGHT_PRESETS, CLASS_BANDS, SPAM_TIER_WEIGHTS
from .spam_llm import spam_counts
from .personalization_llm import personalization_flags
from .tone_llm import tone_flags
from .clarity_llm import clarity_score
from .grammar_llm import grammar_score
from .preprocess import sentences, norm_text, word_count
from .rules import PASSIVE_AGGRESSIVE, HOSTILE
from .comments_llm import subjective_comments

logging.basicConfig(level=logging.ERROR)  # For error logging

# ------------ public helper for UI/CSV order ------------
def metric_keys():
    return ["clarity","length","spam_score","personalization","tone","grammatical_hygiene"]

# ------------ weights / usage utils ------------
def _normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    if not weights:
        weights = DEFAULT_WEIGHT_PRESETS["research_defaults"]
    total = sum(max(0.0, float(v)) for v in weights.values()) or 1.0
    scale = 6.0 / total
    return {k: max(0.0, float(v)) * scale for k, v in weights.items()}

def _safe_sum_usage(u: Any) -> int:
    if not isinstance(u, dict):
        return 0
    return int(u.get("prompt_tokens", 0)) + int(u.get("completion_tokens", 0))

# ------------ deterministic class heuristic ------------
def _infer_class(subject: str, body: str) -> str:
    s = f"{subject} {body}".lower()
    if any(k in s for k in ("invoice","receipt","order #","otp","password reset")): return "transactional"
    if any(k in s for k in ("promo","sale","discount","offer","exclusive","reward","prize","cash","limited time","act now")): return "promo"
    if any(k in s for k in ("follow up","following up","gentle reminder")): return "follow_up"
    if any(k in s for k in ("support","ticket","issue id")): return "support"
    if any(k in s for k in ("intro","nice to meet","partnership","demo","outreach")): return "outreach"
    return "internal_request"

# ------------ length scorer (class-aware) ------------
def _score_length(subject: str, body: str, klass: str) -> Tuple[float, list]:
    cfg = CLASS_BANDS.get(klass, CLASS_BANDS["internal_request"])
    subj_len = len(norm_text(subject))
    wc = word_count(body)

    # subject 0..3 (peak 30–60; soft 20–80)
    smin, smax = 20, 80
    if 30 <= subj_len <= 60:
        subj_score = 3
    elif smin <= subj_len <= smax:
        subj_score = 2
    else:
        subj_score = 1 if subj_len > 0 else 0

    # body 0..7 (ideal band -> 7; good band -> >=4; outside -> down to 0)
    (i_lo, i_hi), (g_lo, g_hi) = cfg["ideal"], cfg["good"]
    if i_lo <= wc <= i_hi:
        bscore = 7.0
    elif g_lo <= wc <= g_hi:
        # linear falloff to 4 at good edges
        span = (g_hi - g_lo) or 1
        dist_from_center = abs(wc - (i_lo + i_hi)/2)
        bscore = max(4.0, 7.0 - 3.0 * (dist_from_center / (span/2)))
    else:
        # quadratic penalty
        d = min(abs(wc - g_lo), abs(wc - g_hi))
        bscore = max(0.0, 4.0 - (d/50.0)**2)

    reasons = [f"subject_len={subj_len}", f"body_wc={wc}", f"class={klass}"]
    return round(max(0.0, min(10.0, subj_score + bscore)), 2), reasons

# ------------ spam scorer ------------
def _score_spam(subject: str, body: str, llm_counts=None, html_ratio_bad=False) -> Tuple[float, list]:
    score = 10.0; reasons=[]
    subj = norm_text(subject); txt = norm_text(body)

    # ALL CAPS subject
    if subj and subj.isupper():
        score -= 2; reasons.append("ALL_CAPS_subject")

    # exclamations
    subj_ex = subj.count("!")
    tot_ex  = subj_ex + txt.count("!")
    if subj_ex > 1: score -= 1; reasons.append("exclam>1_subject")
    if tot_ex > 2:  score -= 1; reasons.append("exclam_total>2")

    # deterministic spam heuristics (urgency/reward/marketing/calls)
    trig = 0.0
    import regex as re2
    from .rules import SPAM_URGENCY, SPAM_REWARD, SPAM_CALLS, SPAM_MARKETING
    if any(re2.search(p, f"{subj} {txt}") for p in SPAM_URGENCY):
        trig += 1.25; reasons.append("urgency_markers")
    if any(re2.search(p, f"{subj} {txt}") for p in SPAM_REWARD):
        trig += 1.5; reasons.append("reward_claims")
    if any(re2.search(p, f"{subj} {txt}") for p in SPAM_CALLS):
        trig += 1.0; reasons.append("clickbait_calls")
    if any(re2.search(p, f"{subj} {txt}") for p in SPAM_MARKETING):
        trig += 0.75; reasons.append("marketing_phrases")
    if trig > 0:
        score -= min(6.0, trig)

    # lexicon (LLM counts only; no profanity lists)
    if llm_counts:
        penal = (llm_counts.get("A",0)*SPAM_TIER_WEIGHTS["A"] +
                 llm_counts.get("B",0)*SPAM_TIER_WEIGHTS["B"] +
                 llm_counts.get("C",0)*SPAM_TIER_WEIGHTS["C"])
        penal = min(penal, 3.0)  # cap lexicon penalty
        if penal > 0:
            score -= penal; reasons.append(f"lexicon_penalty={penal:.2f}")

    # optional HTML heuristic
    if html_ratio_bad:
        score -= 2; reasons.append("low_text_image_ratio")

    # Additional rule for consistency: too many links or URLs
    url_count = len(re.findall(r"https?://", f"{subj} {txt}"))
    if url_count > 3:
        score -= 1; reasons.append(f"too_many_urls={url_count}")

    # If multiple high-risk indicators present, cap at <=6 even before LLM
    if any(r in reasons for r in ("reward_claims","clickbait_calls","urgency_markers")) and (subj.isupper() or txt.count("!") >= 2):
        score = min(score, 6.0)
    return round(max(0.0, min(10.0, score)), 2), reasons

# ------------ personalization scorer ------------
def _score_personalization(subject: str, body: str, cues, too_intrusive: bool) -> Tuple[float, list]:
    count = len(cues)
    relevant = sum(1 for c in cues if c.get("relevant"))
    # degree curve: medium best (research).
    if count == 0: base = 3
    elif count == 1: base = 6 if relevant else 5
    elif count == 2: base = 9 if relevant>=1 else 7
    else: base = 6 if not too_intrusive else 5
    subj_bonus = 1 if any(c.get("relevant") and c.get("text","") in (subject or "") for c in cues) else 0
    score = max(0, min(10, base + subj_bonus))
    reasons = [f"cues={count}", f"relevant={relevant}"] + (["too_intrusive"] if too_intrusive else [])
    return score, reasons

GREETINGS = [r"(?i)^(hi|hello|good (morning|afternoon|evening)|dear)\b"]
SIGNOFFS  = [r"(?i)\b(regards|best|sincerely|thanks|thank you)\b"]

# ------------ tone scorer ------------
def _score_tone(subject: str, body: str, flags: Dict) -> Tuple[float, list]:
    # Base below 10 so bonuses/penalties move meaningfully; audience-aware adjustment later
    score = 8.0; reasons=[]
    if any(re.search(p, body or "") for p in GREETINGS): score += 0.5; reasons.append("greeting")
    if any(re.search(p, body or "") for p in SIGNOFFS): score += 0.5; reasons.append("signoff")

    if (subject or "").isupper(): score -= 2; reasons.append("ALL_CAPS_subject")
    subj_ex = (subject or "").count("!")
    tot_ex  = subj_ex + (body or "").count("!")
    if subj_ex > 1: score -= 1; reasons.append("exclam>1_subject")
    if tot_ex > 2:  score -= 1; reasons.append("exclam_total>2")

    # emojis (simple heuristic)
    emojis = re.findall(r"[\p{Emoji}]", f"{subject or ''} {body or ''}")
    if len(emojis) > 1:
        score -= (len(emojis)-1); reasons.append(f"emoji_extra={len(emojis)-1}")

    # LLM flags
    if flags.get("too_aggressive"): score -= 1.5; reasons.append("too_aggressive")
    if flags.get("overly_casual_for_b2b"): score -= 0.75; reasons.append("overly_casual_for_b2b")
    if flags.get("passive_aggressive_markers"): score -= 0.5; reasons.append("passive_aggressive_markers")

    # Regex-based hostile/passive-aggressive detection
    if any(re.search(p, body or "") for p in HOSTILE):
        score -= 3.0; reasons.append("hostile_language")
    if any(re.search(p, body or "") for p in PASSIVE_AGGRESSIVE):
        score -= 1.0; reasons.append("passive_aggressive_phrasing")

    # Additional rule: polite markers bonus
    polite_count = len(re.findall(r"(?i)\b(please|thank you|thanks|appreciate)\b", body or ""))
    if polite_count > 0:
        score += min(0.25 * polite_count, 0.75); reasons.append(f"polite_markers={polite_count}")

    # Audience-aware adjustment: infer class, then prefer professional tone for business-like classes
    lower_body = (body or "").lower()
    is_family_like = any(k in lower_body for k in ("mom", "dad", "brother", "sister", "family", "love you"))
    if not is_family_like:
        # expect professional tone; penalize excessive informality/hostility further
        if any(re.search(p, body or "") for p in PASSIVE_AGGRESSIVE):
            score -= 0.5
        if any(re.search(p, body or "") for p in HOSTILE):
            score -= 0.5

    # Prevent saturation when negative markers present
    if any(t in reasons for t in ("too_aggressive","overly_casual_for_b2b","passive_aggressive_phrasing","hostile_language")):
        score = min(score, 9.0)
    return round(max(0.0, min(10.0, score)), 2), reasons

# ------------------ main API ------------------
def evaluate(subject: str, body: str, engine: str = "openai", weights: Dict[str, float] = None) -> Dict[str, Any]:
    subject, body = subject or "", body or ""
    engine = engine or "openai"
    W = _normalize_weights(weights or DEFAULT_WEIGHT_PRESETS["research_defaults"])

    # class for length
    klass = _infer_class(subject, body)

    # 1) clarity (LLM-based)
    try:
        c_score, c_details = clarity_score(subject, body, engine)
        c_reasons = [f"ask_signals={len(c_details['llm'].get('ask_signals', []))}", f"subject_useful={c_details['llm'].get('subject_useful', False)}", f"intro_clear={c_details['llm'].get('intro_clear', False)}", "source=llm"]
    except Exception as e:
        logging.error(f"Clarity failed: {e}")
        c_score, c_reasons = 0.0, ["llm_failed"]
    c_usage = c_details.get("usage", {}) if 'c_details' in locals() else {}

    # 2) length
    l_score, l_reasons = _score_length(subject, body, klass)

    # 3) spam (LLM counts + heuristics)
    try:
        sc_counts, sc_usage = spam_counts(subject, body, engine=engine)
    except Exception as e:
        logging.error(f"Spam counts failed: {e}")
        sc_counts, sc_usage = {"A":0,"B":0,"C":0}, {}
    s_score, s_reasons = _score_spam(subject, body, llm_counts=sc_counts, html_ratio_bad=False)

    # 4) personalization (LLM cues + deterministic curve)
    try:
        p_flags, p_usage = personalization_flags(subject, body, engine=engine)
        if not isinstance(p_flags, dict): p_flags = {"cues": [], "too_intrusive": False}
    except Exception as e:
        logging.error(f"Personalization flags failed: {e}")
        p_flags, p_usage = {"cues": [], "too_intrusive": False}, {}
    p_score, p_reasons = _score_personalization(subject, body, p_flags.get("cues", []), bool(p_flags.get("too_intrusive", False)))

    # 5) tone (LLM flags + deterministic math)
    try:
        t_flags, t_usage = tone_flags(subject, body, engine=engine)
        if not isinstance(t_flags, dict):
            t_flags = {"too_aggressive": False, "overly_casual_for_b2b": False, "passive_aggressive_markers": []}
    except Exception as e:
        logging.error(f"Tone flags failed: {e}")
        t_flags, t_usage = {"too_aggressive": False, "overly_casual_for_b2b": False, "passive_aggressive_markers": []}, {}
    t_score, t_reasons = _score_tone(subject, body, t_flags)

    # 6) grammar (LLM-based)
    try:
        g_score, g_reasons, g_usage = grammar_score(subject, body, engine)
    except Exception as e:
        logging.error(f"Grammar failed: {e}")
        g_score, g_reasons, g_usage = 8.0, ["llm_failed"], {}

    # aggregate
    scores = {
        "clarity": float(round(c_score, 2)),
        "length": float(round(l_score, 2)),
        "spam_score": float(round(s_score, 2)),
        "personalization": float(round(p_score, 2)),
        "tone": float(round(t_score, 2)),
        "grammatical_hygiene": float(round(g_score, 2)),
    }
    denom = sum(W.get(k, 0.0) for k in metric_keys()) or 1.0
    weighted_total = float(round(max(0.0, min(10.0, sum(W[k]*scores[k] for k in metric_keys())/denom)), 2))

    explanations = {
        "clarity": c_reasons,
        "length": l_reasons,
        "spam_score": s_reasons,
        "personalization": p_reasons,
        "tone": t_reasons,
        "grammatical_hygiene": g_reasons,
    }

    # usage (only for LLM-backed features that actually ran)
    def _u(x): return _safe_sum_usage(x)
    usage = {"openai_total": 0, "claude_total": 0, "total": 0}
    if engine == "openai":
        usage["openai_total"] = _u(sc_usage) + _u(p_usage) + _u(t_usage) + _u(c_usage) + _u(g_usage)
    else:
        usage["claude_total"] = _u(sc_usage) + _u(p_usage) + _u(t_usage) + _u(c_usage) + _u(g_usage)
    usage["total"] = usage["openai_total"] + usage["claude_total"]

    # subjective LLM comments
    try:
        comm_data, comm_usage = subjective_comments(subject, body, scores, explanations, engine=engine)
    except Exception as e:
        logging.error(f"Subjective comments failed: {e}")
        comm_data, comm_usage = {}, {}
    if engine == "openai":
        usage["openai_total"] += _u(comm_usage)
    else:
        usage["claude_total"] += _u(comm_usage)
    usage["total"] += _u(comm_usage)

    return {
        "class": klass,
        "scores": scores,
        "weighted_total": weighted_total,
        "explanations": explanations,
        "comments": comm_data,
        "usage": usage,
        "meta": {"engine": engine, "weights": W, "version": "2.3"},
    }
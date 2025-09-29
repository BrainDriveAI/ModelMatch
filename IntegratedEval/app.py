"""Unified evaluation UI for Email, Finance, Health, Summary, and Therapy domains.

This module stitches together the existing domain evaluators into a single Gradio
experience so a model can be scored across all five frameworks at once. Each
domain relies on its original evaluation logic; we simply orchestrate the calls,
restrict judge models to GPT-4o and Claude 3.5 Sonnet, and present a concise
summary of the results.
"""

from __future__ import annotations

import json
import os
import statistics
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, List, Tuple

import gradio as gr
import pandas as pd

from openai import OpenAI


# ---------------------------------------------------------------------------
# Import setup – add domain packages to path before importing their modules.
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
for subdir in ["EmailEval", "FinanceEval", "HealthEval", "Summeval", "TherapyEval"]:
    sys.path.append(str(BASE_DIR / subdir))

# Email evaluator
from EmailEval.email_eval.api import evaluate as email_evaluate  # type: ignore
from EmailEval.email_eval.config import DEFAULT_WEIGHT_PRESETS as EMAIL_WEIGHT_PRESETS  # type: ignore

# Finance evaluator
from FinanceEval.core.providers import ProviderKind, get_provider  # type: ignore
from FinanceEval.core.preprocess import normalize_conversation, extract_model_utterances  # type: ignore
from FinanceEval.core.evaluators import evaluate_all_metrics  # type: ignore
from FinanceEval.core.fusion import weighted_total  # type: ignore

# Health evaluator
from HealthEval.core.constants import (
    AVAILABLE_JUDGES,
    DEFAULT_WEIGHTS as HEALTH_DEFAULT_WEIGHTS,
    METRIC_NAMES,
)  # type: ignore
from HealthEval.core.evaluators import HealthEvalEvaluator  # type: ignore
from HealthEval.core.preprocess import Preprocessor  # type: ignore
from HealthEval.core.providers import JudgeProvider  # type: ignore
from HealthEval.core.schema import HealthEvalInput  # type: ignore

# Summary evaluator
from Summeval.src.evaluation import evaluate as summary_evaluate  # type: ignore
from Summeval.src.config import PRESET as SUMMARY_PRESETS  # type: ignore

# Therapy evaluator
from TherapyEval.src.api_clients import BACKENDS as THERAPY_BACKENDS  # type: ignore
from TherapyEval.src.evaluation import evaluate_with_judges  # type: ignore


# ---------------------------------------------------------------------------
# Constants & helpers
# ---------------------------------------------------------------------------
DEFAULT_EMAIL_WEIGHTS = EMAIL_WEIGHT_PRESETS["research_defaults"].copy()
EMAIL_WEIGHT_KEYS = list(DEFAULT_EMAIL_WEIGHTS.keys())


FINANCE_DEFAULT_WEIGHTS = {
    "trust": 0.20,
    "accuracy": 0.25,
    "explain": 0.15,
    "client_first": 0.15,
    "risk_safety": 0.15,
    "clarity": 0.10,
}

SUMMARY_ALLOWED_VARIANTS = list(SUMMARY_PRESETS.keys())
THERAPY_DEFAULT_WEIGHTS: List[float] = [
    0.20,
    0.15,
    0.10,
    0.10,
    0.10,
    0.10,
    0.05,
    0.05,
    0.05,
    0.10,
]

THERAPY_METRIC_NAMES = [
    "Empathy",
    "Emotional Relevance",
    "Tone",
    "Boundary Awareness",
    "Supportiveness",
    "Ethical Safety",
    "Clarity",
    "Consistency",
    "Self-Awareness",
    "Adaptability",
]

SUMMARY_METRIC_NAMES = ["coverage", "alignment", "hallucination", "relevance", "bias_toxicity"]

FINANCE_WEIGHT_KEYS = list(FINANCE_DEFAULT_WEIGHTS.keys())
FINANCE_TOTAL = sum(FINANCE_DEFAULT_WEIGHTS.values()) or 1.0
HEALTH_TOTAL = float(sum(HEALTH_DEFAULT_WEIGHTS)) or 1.0
THERAPY_TOTAL = float(sum(THERAPY_DEFAULT_WEIGHTS)) or 1.0
SUMMARY_TOTALS = {variant: sum(weights.values()) or 1.0 for variant, weights in SUMMARY_PRESETS.items()}
DEFAULT_SUMMARY_VARIANT = SUMMARY_ALLOWED_VARIANTS[0]

CANONICAL_JUDGES = ("GPT-4o", "Claude 3.5 Sonnet")


def _mean(values: List[float]) -> float:
    return float(statistics.mean(values)) if values else 0.0


def _round(value: float) -> float:
    return round(float(value), 2)


def _ensure_text(value: str, label: str) -> str:
    if not value or not value.strip():
        raise ValueError(f"{label} is required.")
    return value


def _empty_scoreboard() -> pd.DataFrame:
    return pd.DataFrame(columns=["Domain", CANONICAL_JUDGES[0], CANONICAL_JUDGES[1], "Domain Avg"])


def _email_weight_inputs(values: Dict[str, float]) -> Dict[str, float]:
    # UI uses 0-10 scale; API expects same range, so passthrough.
    return values


def _finance_weight_inputs(raw: Dict[str, float]) -> Dict[str, float]:
    weights = {
        key: max(0.0, float(raw.get(key, FINANCE_DEFAULT_WEIGHTS[key])))
        for key in FINANCE_DEFAULT_WEIGHTS
    }
    total = sum(weights.values()) or 1.0
    return {k: (v / total) * FINANCE_TOTAL for k, v in weights.items()}


def _health_weight_inputs(raw: List[float]) -> List[float]:
    values = [
        max(0.0, float(raw[idx] if idx < len(raw) else HEALTH_DEFAULT_WEIGHTS[idx]))
        for idx in range(len(METRIC_NAMES))
    ]
    total = sum(values) or 1.0
    return [v / total for v in values]


def _summary_weight_inputs(variant: str, raw: Dict[str, float]) -> Dict[str, float]:
    defaults = _summary_weight_map(variant)
    weights = {k: max(0.0, float(raw.get(k, defaults[k]))) for k in defaults}
    total = sum(weights.values()) or 1.0
    return {k: v / total for k, v in weights.items()}


def _therapy_weight_inputs(raw: List[float]) -> List[float]:
    values = [
        max(0.0, float(raw[idx] if idx < len(raw) else THERAPY_DEFAULT_WEIGHTS[idx]))
        for idx in range(len(THERAPY_DEFAULT_WEIGHTS))
    ]
    total = sum(values) or 1.0
    return [v / total for v in values]


def _email_scores(
    subject: str,
    body: str,
    custom_weights: Dict[str, float] | None = None,
) -> Tuple[float, Dict[str, Dict[str, object]]]:
    per_judge = {}
    for engine, label in (("openai", CANONICAL_JUDGES[0]), ("claude", CANONICAL_JUDGES[1])):
        weights = custom_weights if custom_weights else None
        out = email_evaluate(subject, body, engine=engine, weights=weights)
        per_judge[label] = {
            "score": float(out.get("weighted_total", 0.0)),
            "scores": out.get("scores", {}),
            "comments": out.get("comments", {}),
            "usage": out.get("usage", {}),
        }
    domain_score = _mean([data["score"] for data in per_judge.values()])
    return domain_score, per_judge


def _finance_scores(
    conversation: str,
    custom_weights: Dict[str, float] | None = None,
) -> Tuple[float, Dict[str, Dict[str, object]]]:
    normalized = normalize_conversation(conversation)
    model_only = extract_model_utterances(normalized)
    providers = (
        (ProviderKind.OPENAI, "gpt-4o", CANONICAL_JUDGES[0]),
        (ProviderKind.ANTHROPIC, "claude-3-5-sonnet-20240620", CANONICAL_JUDGES[1]),
    )

    per_judge: Dict[str, Dict[str, object]] = {}
    for kind, model_name, label in providers:
        provider = get_provider(kind, model_name)
        metrics_out, usage, raw_json = evaluate_all_metrics(provider=provider, conversation_text=model_only, alpha_map={})
        weights = custom_weights or FINANCE_DEFAULT_WEIGHTS
        total_score = weighted_total({k: v.get("score_0_10", 0.0) for k, v in metrics_out.items()}, weights)
        per_judge[label] = {
            "score": _round(total_score),
            "metrics": metrics_out,
            "usage": usage,
            "raw": raw_json,
        }

    domain_score = _mean([data["score"] for data in per_judge.values()])
    return domain_score, per_judge


_health_preprocessor = Preprocessor()
_health_judge_provider = JudgeProvider()
_health_evaluator = HealthEvalEvaluator(judge_provider=_health_judge_provider)
_health_judges = [name for name in AVAILABLE_JUDGES.keys() if name in {
    "GPT-4o (OpenAI)",
    "Claude 3.5 Sonnet (Anthropic)",
}]


def _health_scores(
    conversation: str,
    custom_weights: List[float] | None = None,
) -> Tuple[float, Dict[str, Dict[str, object]]]:
    processed = _health_preprocessor.process_query(conversation)
    input_payload = HealthEvalInput(query="Conversation", response=processed)
    weights = custom_weights or HEALTH_DEFAULT_WEIGHTS
    output = _health_evaluator.evaluate(input_payload, weights=weights, selected_judges=_health_judges)

    per_judge: Dict[str, Dict[str, object]] = {}
    for judge_name, data in output.models.items():
        label = CANONICAL_JUDGES[0] if "GPT-4o" in judge_name else CANONICAL_JUDGES[1]
        total_score = float(data.get("total_score", 0.0)) * 2.0  # convert 0–5 average to 0–10 scale
        per_judge[label] = {
            "score": _round(total_score),
            "raw": data,
        }

    domain_score = _mean([data["score"] for data in per_judge.values()])
    return domain_score, per_judge


def _summary_scores(
    article: str,
    summary: str,
    variant: str,
    custom_weights: Dict[str, float] | None = None,
) -> Tuple[float, Dict[str, Dict[str, object]]]:
    preset = SUMMARY_PRESETS[variant]
    weights = custom_weights or preset
    prompts_dir = BASE_DIR / "Summeval" / "prompts"
    prompt_paths = {
        "Twin-Lock": prompts_dir / "twinlock.txt",
        "Judge-Lock": prompts_dir / "judgelock.txt",
    }
    PROMPTS = {name: path.read_text(encoding="utf-8") for name, path in prompt_paths.items()}
    active_backends = ["OpenAI", "Claude"]
    df, feedback, averages, tokens, csv_path, zip_path = summary_evaluate(
        article,
        summary,
        variant,
        active_backends,
        0.0,
        weights["coverage"],
        weights["alignment"],
        weights["hallucination"],
        weights["relevance"],
        weights["bias_toxicity"],
        False,
        PROMPTS,
    )

    per_judge: Dict[str, Dict[str, object]] = {}
    if isinstance(df, pd.DataFrame) and not df.empty:
        for _, row in df.iterrows():
            label = CANONICAL_JUDGES[0] if "OpenAI" in str(row.get("Model")) else CANONICAL_JUDGES[1]
            total = float(row.get("Total", 0.0))
            per_judge[label] = {
                "score": _round(total),
                "metrics": row.to_dict(),
            }

    domain_score = _mean([data["score"] for data in per_judge.values()])
    details = {
        "table": df.to_dict(orient="records") if isinstance(df, pd.DataFrame) else df,
        "feedback": feedback,
        "averages": {k: v for k, v in (averages or {}).items()},
        "tokens": tokens,
        "csv_path": csv_path,
        "zip_path": zip_path,
    }
    for label, data in per_judge.items():
        data.update(details)
        break  # attach shared details once

    return domain_score, per_judge


def _therapy_scores(
    conversation: str,
    custom_weights: List[float] | None = None,
) -> Tuple[float, Dict[str, Dict[str, object]]]:
    weights = custom_weights or THERAPY_DEFAULT_WEIGHTS
    selected = [name for name in THERAPY_BACKENDS.keys() if name in CANONICAL_JUDGES]
    prompt_path = BASE_DIR / "TherapyEval" / "prompts" / "carelock.txt"
    prompt_template = prompt_path.read_text(encoding="utf-8")
    metrics_df, comments, tokens, pros, cons, summary_map, rationales = evaluate_with_judges(
        conversation,
        selected,
        "Care-Lock",
        *weights,
        0.0,
        prompt_template=prompt_template,
    )

    per_judge: Dict[str, Dict[str, object]] = {}
    if isinstance(metrics_df, pd.DataFrame) and not metrics_df.empty:
        for _, row in metrics_df.iterrows():
            label = str(row.get("Model"))
            total = float(row.get("Total", 0.0)) * 10.0
            per_judge[label] = {
                "score": _round(total),
                "metrics": row.to_dict(),
                "comments": comments.get(label, {}),
                "tokens": tokens.get(label),
                "pros": pros.get(label, []),
                "cons": cons.get(label, []),
                "summary": summary_map.get(label, ""),
            }
            if label in rationales:
                per_judge[label]["metric_rationales"] = rationales[label]

    domain_score = _mean([data["score"] for data in per_judge.values()])
    return domain_score, per_judge


def _summary_weight_map(variant: str) -> Dict[str, float]:
    return SUMMARY_PRESETS[variant].copy()


def _score_row(domain: str, per_judge: Dict[str, Dict[str, object]]) -> Dict[str, float]:
    row = {"Domain": domain}
    for judge in CANONICAL_JUDGES:
        row[judge] = _round(per_judge.get(judge, {}).get("score", 0.0))
    row["Domain Avg"] = _round(_mean([per_judge.get(judge, {}).get("score", 0.0) for judge in CANONICAL_JUDGES]))
    return row


def _details_json(per_domain: Dict[str, Dict[str, Dict[str, object]]]) -> Dict[str, object]:
    def _safe(obj):
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict(orient="records")
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, list):
            return obj
        if isinstance(obj, Path):
            return str(obj)
        if isinstance(obj, pd.Series):
            return obj.to_dict()
        if hasattr(obj, "item") and callable(obj.item):
            try:
                return obj.item()
            except Exception:
                pass
        return obj

    return json.loads(json.dumps(per_domain, default=_safe))


def _summarize_details(details: Dict[str, Dict[str, Dict[str, object]]]) -> Dict[str, Dict[str, object]]:
    """Collapse raw per-judge payloads into a consistent community friendly JSON blob."""
    def _stringify(value: object) -> str:
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, dict):
            parts = []
            for key, val in value.items():
                if val is None:
                    continue
                if isinstance(val, (str, int, float)):
                    parts.append(f"{key}: {val}")
                else:
                    parts.append(f"{key}: {json.dumps(val, ensure_ascii=False)}")
            return "; ".join(parts)
        if isinstance(value, (list, tuple, set)):
            return "; ".join(_stringify(item) for item in value if item is not None)
        if value is None:
            return ""
        return str(value)

    def _normalize_metrics(domain: str, payload: Dict[str, object]) -> tuple[Dict[str, float] | None, Dict[str, str] | None]:
        metrics = payload.get("scores") or payload.get("metrics")
        if metrics is None and domain == "Health":
            raw = payload.get("raw")
            if isinstance(raw, dict):
                values = raw.get("scores")
                if isinstance(values, list) and len(values) == len(METRIC_NAMES):
                    metrics = {
                        name: _round(float(score) * 2.0)
                        for name, score in zip(METRIC_NAMES, values)
                    }

        comment_map: Dict[str, str] | None = None
        if metrics is None and domain == "Finance":
            raw = payload.get("raw")
            if isinstance(raw, dict):
                metrics = {}
                comment_map = {}
                for metric in FINANCE_DEFAULT_WEIGHTS:
                    data = raw.get(metric)
                    if not isinstance(data, dict):
                        continue
                    val = data.get("score_0_10") or data.get("score")
                    if isinstance(val, (int, float)):
                        metrics[metric] = val
                    elif val is not None:
                        try:
                            metrics[metric] = float(val)
                        except Exception:
                            continue
                    comment = data.get("comment") or data.get("rationale")
                    if isinstance(comment, str) and comment.strip():
                        comment_map[metric] = comment.strip()
                if not metrics:
                    metrics = None
        if metrics is None:
            return None, comment_map

        normalized: Dict[str, float] = {}
        if comment_map is None:
            comment_map = {}
        if isinstance(metrics, dict):
            for key, value in metrics.items():
                val = value
                extra_comment = None
                if isinstance(value, dict):
                    extra_comment = value.get("rationale") or value.get("comment") or value.get("notes")
                    if "score_0_10" in value:
                        val = value["score_0_10"]
                    elif "score" in value:
                        val = value["score"]
                    elif "value" in value:
                        val = value["value"]
                if isinstance(val, (int, float)):
                    normalized[key] = _round(val)
                else:
                    try:
                        normalized[key] = _round(float(val))
                    except Exception:
                        continue
                if isinstance(extra_comment, str) and extra_comment.strip():
                    comment_map[key] = extra_comment.strip()
        elif isinstance(metrics, (list, tuple)):
            normalized = {
                str(idx): _round(float(val))
                for idx, val in enumerate(metrics, start=1)
                if isinstance(val, (int, float))
            }
        else:
            return None, comment_map

        if domain == "Finance":
            normalized = {k: normalized[k] for k in FINANCE_DEFAULT_WEIGHTS if k in normalized}
        elif domain == "Summary":
            normalized = {k: normalized[k] for k in SUMMARY_METRIC_NAMES if k in normalized}
        elif domain == "Therapy":
            normalized = {k: normalized[k] for k in THERAPY_METRIC_NAMES if k in normalized}
        elif domain == "Health":
            normalized = {k: normalized[k] for k in METRIC_NAMES if k in normalized}

        normalized = normalized or None
        comment_map = {k: v for k, v in (comment_map or {}).items() if v}
        if not comment_map:
            comment_map = None
        if not comment_map and domain == "Therapy":
            rationales = payload.get("metric_rationales")
            if isinstance(rationales, dict):
                comment_map = {k: str(v) for k, v in rationales.items() if v}
            elif isinstance(rationales, list):
                comment_map = {str(idx): str(text) for idx, text in enumerate(rationales, start=1) if text}
        return normalized, comment_map

    def _extract_comment(payload: Dict[str, object]) -> str | None:
        for key in ("summary", "comment", "comments", "feedback", "pros", "cons"):
            value = payload.get(key)
            if value:
                text = _stringify(value)
                if text:
                    return text
        raw = payload.get("raw")
        if isinstance(raw, dict):
            for key in ("summary", "comment", "comments"):
                value = raw.get(key)
                if value:
                    text = _stringify(value)
                    if text:
                        return text
        return None

    def _extract_usage(domain: str, judge: str, payload: Dict[str, object]) -> Dict[str, object] | None:
        usage = payload.get("usage")
        if not usage:
            tokens = payload.get("tokens")
            if isinstance(tokens, (int, float)):
                usage = {"total": tokens}
        if domain == "Summary" and isinstance(usage, dict):
            preferred = "OpenAI" if "GPT" in judge else "Claude"
            if preferred in usage and isinstance(usage.get(preferred), (int, float)):
                usage = {"total": usage[preferred]}
        if isinstance(usage, dict):
            return usage
        if isinstance(usage, (int, float)):
            return {"total": usage}
        return None

    cleaned: Dict[str, Dict[str, object]] = {}
    for domain, judges in details.items():
        domain_info: Dict[str, object] = {}
        for judge_name, payload in judges.items():
            entry: Dict[str, object] = {}

            score = payload.get("score")
            if score is not None:
                entry["score_by_model (sbm)"] = score

            metrics, metric_comments = _normalize_metrics(domain, payload)
            if metrics:
                entry["score_per_metric (spm)"] = metrics

            comment = _extract_comment(payload)
            if not comment and metric_comments:
                summary_prompt = "\n".join(
                    f"Metric: {metric}\nNotes: {text}"
                    for metric, text in metric_comments.items()
                )
                try:
                    comment = _generate_comment(
                        "Write a cohesive evaluation summary using the metric notes below.\n"
                        f"Domain: {domain}\nJudge: {judge_name}\n{summary_prompt}"
                    )
                except Exception:
                    comment = summary_prompt
            if comment:
                entry["overall_comment (comment)"] = comment

            usage = _extract_usage(domain, judge_name, payload)
            if usage:
                entry["token_usage_by_model (tubm)"] = usage

            if entry:
                domain_info[judge_name] = entry

        if domain_info:
            cleaned[domain] = domain_info

    return cleaned


def _generate_comment(prompt: str) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.3,
        messages=[
            {
                "role": "system",
                "content": "You are an evaluator summarizing model performance across multiple metrics."
            },
            {
                "role": "user",
                "content": prompt.strip()
            }
        ],
    )
    return response.choices[0].message.content.strip()

    cleaned: Dict[str, Dict[str, object]] = {}
    for domain, judges in details.items():
        domain_info: Dict[str, object] = {}
        for judge_name, payload in judges.items():
            entry: Dict[str, object] = {}

            score = payload.get("score")
            if score is not None:
                entry["score_by_model (sbm)"] = score

            metrics, metric_comments = _normalize_metrics(domain, payload)
            if metrics:
                entry["score_per_metric (spm)"] = metrics

            comment = _extract_comment(payload)
            if not comment and metric_comments:
                summary_prompt = "\n".join(
                    f"Metric: {metric}\nNotes: {text}"
                    for metric, text in metric_comments.items()
                )
                comment = _generate_comment(
                    "Write a cohesive evaluation summary using the metric notes below.\n"
                    f"Domain: {domain}\nJudge: {judge_name}\n{summary_prompt}"
                )
            if comment:
                entry["overall_comment (comment)"] = comment

            usage = _extract_usage(domain, judge_name, payload)
            if usage:
                entry["token_usage_by_model (tubm)"] = usage

            if entry:
                domain_info[judge_name] = entry

        cleaned[domain] = domain_info

    return cleaned


def run_integrated_eval(*args):
    (
        email_subject,
        email_body,
        email_unfreeze,
        *rest,
    ) = args
    idx = 0
    email_weights = None
    if email_unfreeze:
        raw = {k: rest[idx + i] for i, k in enumerate(EMAIL_WEIGHT_KEYS)}
        email_weights = _email_weight_inputs(raw)
    idx += len(EMAIL_WEIGHT_KEYS)
    finance_conversation = rest[idx]
    idx += 1
    finance_unfreeze = rest[idx]
    idx += 1
    finance_weights = None
    if finance_unfreeze:
        raw_finance = {k: rest[idx + i] for i, k in enumerate(FINANCE_WEIGHT_KEYS)}
        finance_weights = _finance_weight_inputs(raw_finance)
    idx += len(FINANCE_WEIGHT_KEYS)
    health_conversation = rest[idx]
    idx += 1
    health_unfreeze = rest[idx]
    idx += 1
    health_weights = None
    if health_unfreeze:
        raw_health = list(rest[idx: idx + len(METRIC_NAMES)])
        health_weights = _health_weight_inputs(raw_health)
    idx += len(METRIC_NAMES)
    summary_article = rest[idx]
    idx += 1
    summary_text = rest[idx]
    idx += 1
    summary_variant = rest[idx]
    idx += 1
    summary_unfreeze = rest[idx]
    idx += 1
    summary_weights = None
    summary_weight_keys = list(_summary_weight_map(summary_variant).keys())
    if summary_unfreeze:
        raw_summary = {k: rest[idx + i] for i, k in enumerate(summary_weight_keys)}
        summary_weights = _summary_weight_inputs(summary_variant, raw_summary)
    idx += len(summary_weight_keys)
    therapy_conversation = rest[idx]
    idx += 1
    therapy_unfreeze = rest[idx]
    idx += 1
    therapy_weights = None
    if therapy_unfreeze:
        raw_therapy = list(rest[idx: idx + len(THERAPY_DEFAULT_WEIGHTS)])
        therapy_weights = _therapy_weight_inputs(raw_therapy)

    try:
        subject = _ensure_text(email_subject, "Email subject")
        body = _ensure_text(email_body, "Email body")
        finance = _ensure_text(finance_conversation, "Finance conversation")
        health = _ensure_text(health_conversation, "Health conversation")
        article = _ensure_text(summary_article, "Summary article")
        summary = _ensure_text(summary_text, "Summary text")
        therapy = _ensure_text(therapy_conversation, "Therapy conversation")
    except ValueError as exc:
        return _empty_scoreboard(), 0.0, {"error": str(exc)}, str(exc)

    try:
        subject = _ensure_text(email_subject, "Email subject")
        body = _ensure_text(email_body, "Email body")
        finance = _ensure_text(finance_conversation, "Finance conversation")
        health = _ensure_text(health_conversation, "Health conversation")
        article = _ensure_text(summary_article, "Summary article")
        summary = _ensure_text(summary_text, "Summary text")
        therapy = _ensure_text(therapy_conversation, "Therapy conversation")
    except ValueError as exc:
        return _empty_scoreboard(), 0.0, {"error": str(exc)}, str(exc)

    per_domain_details: Dict[str, Dict[str, Dict[str, object]]] = {}
    rows: List[Dict[str, float]] = []

    try:
        email_avg, email_details = _email_scores(subject, body, email_weights)
        per_domain_details["Email"] = email_details
        rows.append(_score_row("Email", email_details))

        finance_avg, finance_details = _finance_scores(finance, finance_weights)
        per_domain_details["Finance"] = finance_details
        rows.append(_score_row("Finance", finance_details))

        health_avg, health_details = _health_scores(health, health_weights)
        per_domain_details["Health"] = health_details
        rows.append(_score_row("Health", health_details))

        summary_avg, summary_details = _summary_scores(article, summary, summary_variant, summary_weights)
        per_domain_details["Summary"] = summary_details
        rows.append(_score_row("Summary", summary_details))

        therapy_avg, therapy_details = _therapy_scores(therapy, therapy_weights)
        per_domain_details["Therapy"] = therapy_details
        rows.append(_score_row("Therapy", therapy_details))

    except Exception as exc:  # pylint: disable=broad-except
        message = f"Evaluation failed: {exc}"
        return _empty_scoreboard(), 0.0, {"error": message}, message

    scoreboard = pd.DataFrame(rows)
    overall = _round(_mean([row["Domain Avg"] for row in rows]))
    details = _summarize_details(_details_json(per_domain_details))
    return scoreboard, overall, details, "Evaluations completed successfully."


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------
with gr.Blocks(title="Integrated Model Evaluation") as demo:
    gr.Markdown(
        """
        # Integrated Model Evaluation
        Provide inputs for each domain and click **Evaluate** to score across all evaluators.
        Judges: GPT-4o and Claude 3.5 Sonnet.
        """
    )

    # Style tweaks: blue sliders + black primary button
    slider_class = "blue-slider"
    gr.HTML(
        """
        <style>
        .blue-slider input[type=range]::-webkit-slider-thumb {background: #1f77b4;}
        .blue-slider input[type=range]::-moz-range-thumb {background: #1f77b4;}
        .blue-slider label {color: #1f77b4;}
        button.primary, .gr-button-primary {background-color: #000000; color: #ffffff;}
        </style>
        """
    )

    initial_summary_weights = _summary_weight_map(SUMMARY_ALLOWED_VARIANTS[0])
    summary_metric_keys = list(initial_summary_weights.keys())

    with gr.Row():
        with gr.Column():
            gr.Markdown("### Email Evaluation")
            email_subject_input = gr.Textbox(label="Email Subject", placeholder="Subject line…")
            email_body_input = gr.Textbox(label="Email Body", lines=8, placeholder="Paste the email body…")
            email_unfreeze = gr.Checkbox(label="Unfreeze default weights", value=False)
            with gr.Group(visible=False) as email_weights_group:
                email_weight_widgets = {
                    metric: gr.Slider(0, 10, value=DEFAULT_EMAIL_WEIGHTS[metric], step=0.5, label=f"{metric.title()} Weight", elem_classes=[slider_class])
                    for metric in DEFAULT_EMAIL_WEIGHTS
                }
            email_unfreeze.change(
                lambda checked: gr.update(visible=checked),
                inputs=email_unfreeze,
                outputs=email_weights_group,
            )

        with gr.Column():
            gr.Markdown("### Finance Evaluation")
            finance_conversation_input = gr.Textbox(
                label="Finance Conversation",
                lines=10,
                placeholder="Paste the advisor conversation transcript…",
            )
            finance_unfreeze = gr.Checkbox(label="Unfreeze default weights", value=False)
            with gr.Group(visible=False) as finance_weights_group:
                finance_weight_widgets = {
                    metric: gr.Slider(0.0, 10.0, value=FINANCE_DEFAULT_WEIGHTS[metric] * 10 / FINANCE_TOTAL, step=0.1, label=f"{metric.replace('_', ' ').title()} Weight", elem_classes=[slider_class])
                    for metric in FINANCE_DEFAULT_WEIGHTS
                }
            finance_unfreeze.change(
                lambda checked: gr.update(visible=checked),
                inputs=finance_unfreeze,
                outputs=finance_weights_group,
            )

    with gr.Row():
        with gr.Column():
            gr.Markdown("### Health Evaluation")
            health_conversation_input = gr.Textbox(
                label="Health Conversation",
                lines=10,
                placeholder="Paste the health support dialogue…",
            )
            health_unfreeze = gr.Checkbox(label="Unfreeze default weights", value=False)
            with gr.Group(visible=False) as health_weights_group:
                health_weight_widgets = [
                    gr.Slider(0.0, 10.0, value=HEALTH_DEFAULT_WEIGHTS[i], step=0.1, label=name, elem_classes=[slider_class])
                    for i, name in enumerate(METRIC_NAMES)
                ]
            health_unfreeze.change(
                lambda checked: gr.update(visible=checked),
                inputs=health_unfreeze,
                outputs=health_weights_group,
            )

        with gr.Column():
            gr.Markdown("### Therapy Evaluation")
            therapy_conversation_input = gr.Textbox(
                label="Therapy Conversation",
                lines=10,
                placeholder="Paste the therapy-style conversation…",
            )
            therapy_unfreeze = gr.Checkbox(label="Unfreeze default weights", value=False)
            with gr.Group(visible=False) as therapy_weights_group:
                therapy_weight_widgets = [
                    gr.Slider(0.0, 10.0, value=THERAPY_DEFAULT_WEIGHTS[i], step=0.1, label=THERAPY_METRIC_NAMES[i], elem_classes=[slider_class])
                    for i in range(len(THERAPY_DEFAULT_WEIGHTS))
                ]
            therapy_unfreeze.change(
                lambda checked: gr.update(visible=checked),
                inputs=therapy_unfreeze,
                outputs=therapy_weights_group,
            )

    with gr.Column():
        gr.Markdown("### Summary Evaluation")
        summary_article_input = gr.Textbox(label="Article / Source Text", lines=8, placeholder="Paste the source article…")
        summary_text_input = gr.Textbox(label="Model Summary", lines=6, placeholder="Paste the model's summary output…")
        summary_variant_input = gr.Dropdown(
            SUMMARY_ALLOWED_VARIANTS,
            value=SUMMARY_ALLOWED_VARIANTS[0],
            label="Evaluation Variant",
        )
        summary_unfreeze = gr.Checkbox(label="Unfreeze default weights", value=False)
        with gr.Group(visible=False) as summary_weights_group:
            summary_weight_widgets = {
                metric: gr.Slider(0.0, 10.0, value=initial_summary_weights[metric], step=0.1, label=f"{metric.replace('_',' ').title()} Weight", elem_classes=[slider_class])
                for metric in summary_metric_keys
            }

        def _toggle_summary_weights(checked, variant):
            updates = [gr.update(visible=checked)]
            if checked:
                weights = _summary_weight_map(variant)
                updates.extend([gr.update(value=weights[key]) for key in summary_metric_keys])
            else:
                updates.extend([gr.update() for _ in summary_metric_keys])
            return updates

        summary_unfreeze.change(
            lambda checked, variant: _toggle_summary_weights(checked, variant),
            inputs=[summary_unfreeze, summary_variant_input],
            outputs=[summary_weights_group, *summary_weight_widgets.values()],
        )

        summary_variant_input.change(
            lambda variant, checked: _toggle_summary_weights(checked, variant),
            inputs=[summary_variant_input, summary_unfreeze],
            outputs=[summary_weights_group, *summary_weight_widgets.values()],
        )

    evaluate_button = gr.Button("Evaluate All Domains", variant="primary")
    gr.HTML(
        """
        <style>
        button.primary, .gr-button-primary {background-color: #000000; color: #ffffff;}
        </style>
        """
    )

    scores_table = gr.Dataframe(label="Domain Scores", interactive=False)
    overall_score = gr.Number(label="Overall Average Score (0–10)", precision=2)
    details_json = gr.JSON(label="Per-Domain Details")
    status_box = gr.Textbox(label="Status", interactive=False)

    evaluate_button.click(
        fn=run_integrated_eval,
        inputs=[
            email_subject_input,
            email_body_input,
            email_unfreeze,
            *(email_weight_widgets.values()),
            finance_conversation_input,
            finance_unfreeze,
            *(finance_weight_widgets.values()),
            health_conversation_input,
            health_unfreeze,
            *health_weight_widgets,
            summary_article_input,
            summary_text_input,
            summary_variant_input,
            summary_unfreeze,
            *(summary_weight_widgets.values()),
            therapy_conversation_input,
            therapy_unfreeze,
            *therapy_weight_widgets,
        ],
        outputs=[scores_table, overall_score, details_json, status_box],
    )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=3000, show_error=True)


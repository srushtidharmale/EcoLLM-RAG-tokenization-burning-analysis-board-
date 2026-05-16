"""Simulated multi-tier LLM inference for demo (no GPU/API required)."""

from __future__ import annotations

import time
from dataclasses import dataclass

from ecollm.rag import RetrievalResult
from ecollm.router import RoutingDecision

MODEL_LABELS = {
    "tiny": "TinyLlama-1.1B (simulated)",
    "small": "Phi-3-mini (simulated)",
    "large": "Mistral-7B-Instruct (simulated)",
}

# Simulated quality score 0-1 by tier and whether RAG was used appropriately
TIER_BASE_QUALITY = {"tiny": 0.72, "small": 0.85, "large": 0.93}


@dataclass
class InferenceResult:
    answer: str
    input_tokens: int
    output_tokens: int
    model_label: str
    quality_score: float


def _estimate_tokens(text: str) -> int:
    return max(1, int(len(text.split()) * 1.3))


def _pick_template(query: str, context: str, tier: str) -> str:
    q_lower = query.lower()
    if any(g in q_lower for g in ("hi", "hello", "hey")):
        return (
            "Hello! I'm EcoLLM-RAG running in **energy-saver mode**. "
            "I routed your greeting to a tiny model with **zero retrieval** — "
            "that's how systems like Claude burn fewer tokens on simple chats."
        )
    if "token" in q_lower or "burn" in q_lower or "energy" in q_lower:
        return (
            "**Token burning** happens on every API call: input tokens (your prompt + RAG context) "
            "+ output tokens (the reply). Bigger models and full-context RAG multiply cost.\n\n"
            "This demo **reduces burning** by: (1) skipping RAG when unnecessary, "
            "(2) compressing context, (3) routing simple queries to TinyLlama-tier models, "
            "(4) capping output length, and (5) using 4-bit-style efficient tiers when possible."
        )
    if context:
        snippet = context[:400] + ("..." if len(context) > 400 else "")
        return (
            f"Based on retrieved Green-AI knowledge ({MODEL_LABELS[tier]}):\n\n"
            f"{snippet}\n\n"
            f"**Summary:** Your question about «{query[:60]}...» is answered using "
            f"{'compressed ' if len(context.split()) < 100 else ''}RAG context "
            f"with an energy-efficient {tier} model tier."
        )
    return (
        f"Direct answer ({MODEL_LABELS[tier]}): "
        f"For «{query[:80]}», no document retrieval was needed — "
        f"saving embedding compute and ~{30 + len(query.split())} input tokens vs full RAG."
    )


def run_inference(
    query: str,
    routing: RoutingDecision,
    retrieval: RetrievalResult,
) -> InferenceResult:
    """Simulate generation with tier-appropriate delay and token counts."""
    context = retrieval.compressed_context if routing.use_rag else ""
    prompt = f"System: Green AI assistant.\nUser: {query}\n"
    if context:
        prompt += f"Context:\n{context}\n"

    input_tokens = _estimate_tokens(prompt)
    if not routing.use_rag and not context:
        input_tokens = _estimate_tokens(query) + 12

    # Simulate compute time proportional to tier
    delay = {"tiny": 0.05, "small": 0.12, "large": 0.28}[routing.model_tier]
    if routing.use_rag and not retrieval.retrieval_skipped:
        delay += 0.08
    time.sleep(delay)

    answer = _pick_template(query, context, routing.model_tier)
    words = answer.split()
    max_out = routing.max_output_tokens
    if len(words) > max_out // 1.3:
        answer = " ".join(words[: int(max_out / 1.3)]) + "..."
    output_tokens = min(_estimate_tokens(answer), routing.max_output_tokens)

    quality = TIER_BASE_QUALITY[routing.model_tier]
    if routing.use_rag and retrieval.chunks and not retrieval.retrieval_skipped:
        quality += 0.05
    if routing.compress_context and context:
        quality += 0.02
    quality = min(0.98, quality)

    return InferenceResult(
        answer=answer,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        model_label=MODEL_LABELS[routing.model_tier],
        quality_score=round(quality, 3),
    )


def run_baseline_inference(query: str, rag) -> InferenceResult:
    """Wasteful path: always large model + full uncompressed RAG."""
    retrieval = rag.build_context(query, skip=False, compress=False)
    full_ctx = "\n\n".join(retrieval.chunks) if retrieval.chunks else ""
    prompt = f"System.\nUser: {query}\nContext:\n{full_ctx}\n"
    input_tokens = _estimate_tokens(prompt) + 200  # extra system overhead
    time.sleep(0.06)
    answer = _pick_template(query, full_ctx or "full knowledge base", "large")
    output_tokens = min(512, _estimate_tokens(answer) + 80)
    return InferenceResult(
        answer=answer,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        model_label=MODEL_LABELS["large"] + " [baseline]",
        quality_score=0.94,
    )

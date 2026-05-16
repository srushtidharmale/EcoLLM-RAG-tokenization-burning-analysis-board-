"""Energy-aware query router: picks model tier and inference strategy."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class Strategy(str, Enum):
    SMALL_DIRECT = "small_model_direct"
    RAG_SMALL = "rag_small_model"
    RAG_LARGE = "rag_large_model"
    COMPRESSED_RAG = "compressed_rag_small"
    BASELINE_WASTEFUL = "baseline_large_full_rag"


class QueryDifficulty(str, Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


@dataclass
class RoutingDecision:
    difficulty: QueryDifficulty
    strategy: Strategy
    model_tier: str
    use_rag: bool
    compress_context: bool
    max_output_tokens: int
    reason: str


# Patterns suggesting retrieval is needed
RAG_TRIGGERS = re.compile(
    r"\b(what|how|why|explain|compare|research|paper|study|data|"
    r"statistics|according|source|evidence|green ai|rag|quantization|"
    r"codecarbon|neuromorphic|photonic|flashattention|distillation)\b",
    re.I,
)

COMPLEX_TRIGGERS = re.compile(
    r"\b(compare|versus|vs\.|trade.?off|analyze|evaluate|multi.?step|"
    r"pros and cons|architecture|design a|implement)\b",
    re.I,
)

GREETING = re.compile(r"^(hi|hello|hey|thanks|thank you|bye)\b", re.I)


def classify_difficulty(query: str) -> QueryDifficulty:
    q = query.strip()
    if len(q) < 20 or GREETING.match(q):
        return QueryDifficulty.SIMPLE
    if COMPLEX_TRIGGERS.search(q) or len(q) > 180:
        return QueryDifficulty.COMPLEX
    if RAG_TRIGGERS.search(q):
        return QueryDifficulty.MEDIUM
    return QueryDifficulty.SIMPLE


def needs_retrieval(query: str, difficulty: QueryDifficulty) -> bool:
    if difficulty == QueryDifficulty.SIMPLE and not RAG_TRIGGERS.search(query):
        return False
    return bool(RAG_TRIGGERS.search(query)) or difficulty != QueryDifficulty.SIMPLE


def route_query(query: str, energy_saver_mode: bool = True) -> RoutingDecision:
    """Choose the most efficient path that can still answer the query."""
    difficulty = classify_difficulty(query)
    use_rag = needs_retrieval(query, difficulty)

    if not energy_saver_mode:
        return RoutingDecision(
            difficulty=difficulty,
            strategy=Strategy.BASELINE_WASTEFUL,
            model_tier="large",
            use_rag=True,
            compress_context=False,
            max_output_tokens=512,
            reason="Baseline: always Mistral-scale model + full RAG (like typical Claude/API usage).",
        )

    if difficulty == QueryDifficulty.SIMPLE and not use_rag:
        return RoutingDecision(
            difficulty=difficulty,
            strategy=Strategy.SMALL_DIRECT,
            model_tier="tiny",
            use_rag=False,
            compress_context=False,
            max_output_tokens=128,
            reason="Simple query → TinyLlama direct, no retrieval (saves embedding + context tokens).",
        )

    if difficulty == QueryDifficulty.MEDIUM or (use_rag and difficulty != QueryDifficulty.COMPLEX):
        return RoutingDecision(
            difficulty=difficulty,
            strategy=Strategy.COMPRESSED_RAG,
            model_tier="small",
            use_rag=True,
            compress_context=True,
            max_output_tokens=256,
            reason="Medium query → compressed RAG + Phi-3-class model.",
        )

    if difficulty == QueryDifficulty.COMPLEX:
        return RoutingDecision(
            difficulty=difficulty,
            strategy=Strategy.RAG_LARGE,
            model_tier="large",
            use_rag=True,
            compress_context=True,
            max_output_tokens=384,
            reason="Complex query → compressed RAG + Mistral-7B only when needed.",
        )

    return RoutingDecision(
        difficulty=difficulty,
        strategy=Strategy.RAG_SMALL,
        model_tier="small",
        use_rag=use_rag,
        compress_context=True,
        max_output_tokens=200,
        reason="Default efficient path → small model + adaptive RAG.",
    )

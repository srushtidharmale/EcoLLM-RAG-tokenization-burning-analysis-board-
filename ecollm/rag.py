"""Lightweight adaptive RAG with optional prompt compression."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class RetrievalResult:
    chunks: List[str]
    scores: List[float]
    compressed_context: str
    retrieval_skipped: bool
    input_tokens_estimate: int


class AdaptiveRAG:
    def __init__(self, knowledge_path: Path, top_k: int = 3):
        self.top_k = top_k
        self.chunks: List[str] = []
        self._vectorizer: TfidfVectorizer | None = None
        self._matrix = None
        self._load(knowledge_path)

    def _load(self, path: Path) -> None:
        text = path.read_text(encoding="utf-8")
        self.chunks = [p.strip() for p in text.split("\n\n") if p.strip()]
        if not self.chunks:
            self.chunks = [line.strip() for line in text.splitlines() if line.strip()]
        self._vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
        self._matrix = self._vectorizer.fit_transform(self.chunks)

    def retrieve(self, query: str, skip: bool = False) -> RetrievalResult:
        if skip or not self.chunks:
            return RetrievalResult(
                chunks=[],
                scores=[],
                compressed_context="",
                retrieval_skipped=True,
                input_tokens_estimate=0,
            )

        q_vec = self._vectorizer.transform([query])
        sims = cosine_similarity(q_vec, self._matrix).flatten()
        top_idx = np.argsort(sims)[::-1][: self.top_k]
        selected = [(self.chunks[i], float(sims[i])) for i in top_idx if sims[i] > 0.05]

        if not selected:
            return RetrievalResult(
                chunks=[],
                scores=[],
                compressed_context="",
                retrieval_skipped=True,
                input_tokens_estimate=0,
            )

        chunks = [c for c, _ in selected]
        scores = [s for _, s in selected]
        return RetrievalResult(
            chunks=chunks,
            scores=scores,
            compressed_context="",
            retrieval_skipped=False,
            input_tokens_estimate=sum(len(c.split()) for c in chunks),
        )

    @staticmethod
    def compress_chunks(chunks: List[str], max_words: int = 80) -> str:
        """Prompt compression: merge chunks and trim to token budget."""
        merged = " ".join(chunks)
        words = merged.split()
        if len(words) <= max_words:
            return merged
        # Keep first and highest-signal sentences
        sentences = [s.strip() for s in merged.replace(";", ".").split(".") if s.strip()]
        out: List[str] = []
        count = 0
        for sent in sentences:
            w = len(sent.split())
            if count + w > max_words:
                break
            out.append(sent)
            count += w
        text = ". ".join(out)
        if text and not text.endswith("."):
            text += "."
        return text or " ".join(words[:max_words])

    def build_context(
        self, query: str, skip: bool, compress: bool
    ) -> RetrievalResult:
        result = self.retrieve(query, skip=skip)
        if result.retrieval_skipped:
            return result
        if compress:
            result.compressed_context = self.compress_chunks(result.chunks, max_words=70)
            result.input_tokens_estimate = len(result.compressed_context.split())
        else:
            result.compressed_context = "\n\n".join(result.chunks)
            result.input_tokens_estimate = sum(len(c.split()) for c in result.chunks)
        return result

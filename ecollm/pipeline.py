"""EcoLLM-RAG orchestration: route → RAG → infer → track energy."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from ecollm.energy_tracker import EnergyTracker, simulate_latency_ms
from ecollm.inference import InferenceResult, run_baseline_inference, run_inference
from ecollm.rag import AdaptiveRAG
from ecollm.router import RoutingDecision, route_query


@dataclass
class QueryResult:
    query: str
    answer: str
    routing: RoutingDecision
    inference: InferenceResult
    metrics: Dict[str, Any]
    baseline_metrics: Optional[Dict[str, Any]] = None
    retrieval_skipped: bool = False
    context_preview: str = ""


class EcoLLMPipeline:
    def __init__(self, knowledge_path: Optional[Path] = None, region: str = "global_avg"):
        root = Path(__file__).resolve().parent.parent
        kb = knowledge_path or root / "data" / "knowledge_base.txt"
        self.rag = AdaptiveRAG(kb)
        self.tracker = EnergyTracker(region=region)
        self.history: List[QueryResult] = []

    def process(
        self,
        query: str,
        energy_saver_mode: bool = True,
        compare_baseline: bool = True,
    ) -> QueryResult:
        routing = route_query(query, energy_saver_mode=energy_saver_mode)

        with self.tracker.track_compute():
            t0 = time.perf_counter()
            retrieval = self.rag.build_context(
                query,
                skip=not routing.use_rag,
                compress=routing.compress_context,
            )
            inference = run_inference(query, routing, retrieval)
            elapsed_ms = (time.perf_counter() - t0) * 1000

        rag_steps = 0 if retrieval.retrieval_skipped else 1
        sim_lat = simulate_latency_ms(
            routing.model_tier,
            inference.input_tokens + inference.output_tokens,
            rag_steps=rag_steps,
        )
        latency_ms = max(elapsed_ms, sim_lat * 0.3)

        metrics = self.tracker.estimate_from_tokens(
            inference.input_tokens,
            inference.output_tokens,
            routing.model_tier,
            latency_ms,
            strategy=routing.strategy.value,
        )

        baseline_metrics = None
        if compare_baseline and energy_saver_mode:
            baseline_inf = run_baseline_inference(query, self.rag)
            b_tokens = baseline_inf.input_tokens + baseline_inf.output_tokens
            b_rate = 1.2 / 1000 * b_tokens
            b_lat = simulate_latency_ms("large", b_tokens, rag_steps=1)
            baseline_metrics = {
                "total_tokens": b_tokens,
                "energy_wh": b_rate,
                "latency_ms": b_lat,
                "model": baseline_inf.model_label,
            }
            metrics = self.tracker.compare_to_baseline(
                metrics,
                baseline_tokens=b_tokens,
                baseline_energy_wh=b_rate,
                baseline_latency_ms=b_lat,
            )

        result = QueryResult(
            query=query,
            answer=inference.answer,
            routing=routing,
            inference=inference,
            metrics=metrics.to_dict(),
            baseline_metrics=baseline_metrics,
            retrieval_skipped=retrieval.retrieval_skipped,
            context_preview=(retrieval.compressed_context or "")[:300],
        )
        self.history.append(result)
        return result

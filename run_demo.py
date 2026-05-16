#!/usr/bin/env python3
"""CLI live demonstration of EcoLLM-RAG energy savings."""

from ecollm.pipeline import EcoLLMPipeline


def main():
    pipeline = EcoLLMPipeline()
    queries = [
        "Hi there!",
        "What is token burning in AI APIs?",
        "Explain Green AI and quantization for lower energy.",
        "Compare adaptive RAG vs always-on retrieval for sustainability.",
    ]

    print("=" * 60)
    print("EcoLLM-RAG — Green AI Live CLI Demo")
    print("=" * 60)

    for q in queries:
        print(f"\n>>> Query: {q}")
        r = pipeline.process(q, energy_saver_mode=True, compare_baseline=True)
        m = r.metrics
        print(f"    Model: {r.inference.model_label}")
        print(f"    Strategy: {r.routing.strategy.value}")
        print(f"    Tokens: {m['total_tokens']} | Latency: {m['latency_ms']:.0f}ms | Energy: {m['energy_wh']*1000:.3f} mWh")
        if r.baseline_metrics:
            print(f"    vs Baseline — Energy saved: {m.get('energy_saved_pct', 0):.1f}% | Tokens saved: {m.get('tokens_saved_vs_baseline', 0)}")
        print(f"    Answer preview: {r.answer[:120]}...")

    print("\n" + "=" * 60)
    print("Start live dashboard: streamlit run app/dashboard.py")
    print("=" * 60)


if __name__ == "__main__":
    main()

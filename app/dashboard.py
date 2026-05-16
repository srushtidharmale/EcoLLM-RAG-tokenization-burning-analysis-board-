"""
EcoLLM-RAG Live Dashboard
Green AI: Reducing token-level energy consumption through efficient LLM inference.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ecollm.pipeline import EcoLLMPipeline

st.set_page_config(
    page_title="EcoLLM-RAG | Green AI Dashboard",
    page_icon="🌿",
    layout="wide",
)

CO2_FACTORS = {
    "global_avg": 0.475,
    "us_avg": 0.386,
    "eu_avg": 0.276,
    "renewable": 0.05,
    "coal_heavy": 0.82,
}

DEMO_QUERIES = [
    "Hi there!",
    "What is token burning in AI APIs?",
    "Explain Green AI and how quantization reduces energy.",
    "Compare adaptive RAG vs always-on retrieval for sustainability.",
]

st.markdown(
    """
    <style>
    .main-header { font-size: 2rem; font-weight: 700; color: #1b5e20; }
    .savings { color: #2e7d32; font-weight: 600; }
    .hint { background: #e8f5e9; padding: 12px 16px; border-radius: 8px; border-left: 4px solid #2e7d32; }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_session():
    if "pipeline" not in st.session_state:
        pipe = EcoLLMPipeline()
        pipe.tracker.use_codecarbon = False  # fast, reliable UI runs
        st.session_state.pipeline = pipe
    if "session_log" not in st.session_state:
        st.session_state.session_log = []
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "query_input" not in st.session_state:
        st.session_state.query_input = DEMO_QUERIES[0]
    if "bootstrapped" not in st.session_state:
        st.session_state.bootstrapped = True
        st.session_state.trigger_run = True


def run_query(query: str, energy_saver: bool, compare: bool):
    try:
        return st.session_state.pipeline.process(
            query.strip(),
            energy_saver_mode=energy_saver,
            compare_baseline=compare,
        )
    except Exception as exc:
        st.error(f"Run failed: {exc}")
        return None


def render_header():
    st.markdown('<p class="main-header">🌿 EcoLLM-RAG — Green AI Live Dashboard</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hint"><b>How to use:</b> Click a demo on the left sidebar '
        "(runs automatically) or type a question and press <b>Run EcoLLM</b>.</p>",
        unsafe_allow_html=True,
    )


def render_sidebar() -> tuple[bool, bool]:
    with st.sidebar:
        st.header("⚙️ Controls")
        energy_saver = st.toggle("Energy Saver Mode", value=True, key="energy_saver")
        compare = st.toggle("Compare vs Baseline", value=True, key="compare_baseline")
        region = st.selectbox("Carbon intensity region", list(CO2_FACTORS.keys()), index=0, key="carbon_region")
        st.session_state.pipeline.tracker.region = region
        st.session_state.pipeline.tracker._co2_factor = CO2_FACTORS[region]

        st.divider()
        st.subheader("Demo queries (click to run)")
        for i, demo in enumerate(DEMO_QUERIES):
            if st.button(demo, key=f"demo_btn_{i}", use_container_width=True):
                st.session_state.query_input = demo
                st.session_state.trigger_run = True

        st.divider()
        st.caption(
            "Modules: energy router · adaptive RAG · prompt compression · token budget"
        )
    return energy_saver, compare


def render_result(result):
    st.markdown("### 📊 Results")
    m = result.metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Model", result.inference.model_label.split("(")[0].strip())
    with col2:
        saved = m.get("tokens_saved_vs_baseline", 0)
        st.metric("Total tokens", m["total_tokens"], delta=f"-{saved} saved" if saved else None)
    with col3:
        lp = m.get("latency_saved_pct", 0)
        st.metric("Latency (ms)", f"{m['latency_ms']:.0f}", delta=f"-{lp:.0f}%" if lp else None)
    with col4:
        ep = m.get("energy_saved_pct", 0)
        st.metric("Energy (mWh)", f"{m['energy_wh'] * 1000:.3f}", delta=f"-{ep:.0f}%" if ep else None)
    with col5:
        st.metric("CO₂ (mg)", f"{m['co2_g'] * 1000:.3f}")

    st.success(f"**Strategy:** `{result.routing.strategy.value}` — {result.routing.reason}")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Answer")
        st.markdown(result.answer)
    with c2:
        st.subheader("Routing & efficiency")
        st.json(
            {
                "difficulty": result.routing.difficulty.value,
                "model_tier": result.routing.model_tier,
                "use_rag": result.routing.use_rag,
                "compress_context": result.routing.compress_context,
                "max_output_tokens": result.routing.max_output_tokens,
                "retrieval_skipped": result.retrieval_skipped,
                "quality_score": result.inference.quality_score,
            }
        )
        if result.context_preview:
            st.text_area("Retrieved context (compressed)", result.context_preview, height=120, disabled=True)

    if result.baseline_metrics:
        st.subheader("Optimized vs Baseline (always large + full RAG)")
        b = result.baseline_metrics
        fig = go.Figure()
        labels = ["Tokens", "Energy (mWh)", "Latency (ms)"]
        opt = [m["total_tokens"], m["energy_wh"] * 1000, m["latency_ms"]]
        base = [b["total_tokens"], b["energy_wh"] * 1000, b["latency_ms"]]
        fig.add_trace(go.Bar(name="EcoLLM (optimized)", x=labels, y=opt, marker_color="#43a047"))
        fig.add_trace(go.Bar(name="Baseline (wasteful)", x=labels, y=base, marker_color="#e53935"))
        fig.update_layout(barmode="group", height=340, margin=dict(t=30))
        st.plotly_chart(fig, use_container_width=True)

        s1, s2, s3, s4 = st.columns(4)
        s1.markdown(f'<p class="savings">Tokens saved: {m.get("tokens_saved_vs_baseline", 0)}</p>', unsafe_allow_html=True)
        s2.markdown(f'<p class="savings">Energy ↓ {m.get("energy_saved_pct", 0):.1f}%</p>', unsafe_allow_html=True)
        s3.markdown(f'<p class="savings">Latency ↓ {m.get("latency_saved_pct", 0):.1f}%</p>', unsafe_allow_html=True)
        s4.markdown(f'<p class="savings">Quality: {result.inference.quality_score:.0%}</p>', unsafe_allow_html=True)


def render_session_charts():
    log = st.session_state.session_log
    if not log:
        return
    st.divider()
    st.subheader("Session analytics")
    df = pd.DataFrame(
        [
            {
                "query": r.query[:40],
                "tokens": r.metrics["total_tokens"],
                "energy_mwh": r.metrics["energy_wh"] * 1000,
                "latency_ms": r.metrics["latency_ms"],
                "strategy": r.routing.strategy.value,
                "saved_pct": r.metrics.get("energy_saved_pct", 0),
            }
            for r in log
        ]
    )
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(
            px.line(df, x=df.index, y="tokens", markers=True, title="Tokens per query"),
            use_container_width=True,
        )
    with c2:
        st.plotly_chart(
            px.bar(
                df,
                x="query",
                y="saved_pct",
                title="Energy saved % vs baseline",
                color="saved_pct",
                color_continuous_scale="Greens",
            ),
            use_container_width=True,
        )
    st.dataframe(df, use_container_width=True)


def main():
    init_session()
    render_header()
    energy_saver, compare = render_sidebar()

    with st.expander("System architecture"):
        st.code(
            "Query → Classifier → Energy Router → Adaptive RAG → Model Tier → Metrics → Dashboard",
            language="text",
        )

    st.text_input(
        "Ask a research question",
        key="query_input",
        placeholder="e.g. How does adaptive RAG reduce token burning?",
    )

    col_run, col_clear = st.columns([1, 1])
    with col_run:
        run_clicked = st.button("▶ Run EcoLLM", type="primary", key="run_ecollm_btn", use_container_width=True)
    with col_clear:
        if st.button("Clear results", key="clear_btn", use_container_width=True):
            st.session_state.last_result = None
            st.session_state.session_log = []
            st.rerun()

    should_run = run_clicked or st.session_state.pop("trigger_run", False)
    query = st.session_state.query_input.strip()

    if should_run:
        if query:
            with st.spinner("Running: classify → route → RAG → infer → measure energy..."):
                result = run_query(query, energy_saver, compare)
            if result:
                st.session_state.last_result = result
                st.session_state.session_log.append(result)
        else:
            st.warning("Type a question or click a sidebar demo.")

    if st.session_state.last_result:
        render_result(st.session_state.last_result)
    elif not should_run:
        st.info("👈 Click **Hi there!** in the sidebar or press **Run EcoLLM** to start the live demo.")

    render_session_charts()

    with st.expander("About this research project"):
        st.markdown(
            "**Research question:** Can an energy-aware RAG system reduce tokens, latency, "
            "and estimated CO₂ while maintaining answer quality?"
        )


if __name__ == "__main__":
    main()

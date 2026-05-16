"""Energy and carbon estimation for LLM inference paths."""

from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Generator, Optional

# Wh per 1K tokens — illustrative values from efficiency literature / HF energy work
ENERGY_WH_PER_1K_TOKENS = {
    "tiny": 0.08,
    "small": 0.25,
    "large": 1.2,
}

# g CO2 per Wh (global grid average ~0.4-0.5; use 0.475)
CO2_G_PER_WH = 0.475

CARBON_INTENSITY_REGIONS = {
    "global_avg": 0.475,
    "us_avg": 0.386,
    "eu_avg": 0.276,
    "coal_heavy": 0.82,
    "renewable": 0.05,
}


@dataclass
class EnergyMetrics:
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0.0
    energy_wh: float = 0.0
    co2_g: float = 0.0
    model_tier: str = "tiny"
    strategy: str = ""
    codecarbon_wh: float = 0.0
    tokens_saved_vs_baseline: int = 0
    energy_saved_pct: float = 0.0
    latency_saved_pct: float = 0.0

    def to_dict(self) -> dict:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "latency_ms": round(self.latency_ms, 2),
            "energy_wh": round(self.energy_wh, 6),
            "co2_g": round(self.co2_g, 6),
            "model_tier": self.model_tier,
            "strategy": self.strategy,
            "codecarbon_wh": round(self.codecarbon_wh, 6),
            "tokens_saved_vs_baseline": self.tokens_saved_vs_baseline,
            "energy_saved_pct": round(self.energy_saved_pct, 1),
            "latency_saved_pct": round(self.latency_saved_pct, 1),
        }


@dataclass
class EnergyTracker:
    region: str = "global_avg"
    use_codecarbon: bool = True
    _codecarbon_emissions: Optional[object] = field(default=None, repr=False)

    def __post_init__(self) -> None:
        self._co2_factor = CARBON_INTENSITY_REGIONS.get(self.region, CO2_G_PER_WH)

    @contextmanager
    def track_compute(self) -> Generator[None, None, None]:
        """Wrap CPU work with CodeCarbon when available."""
        if not self.use_codecarbon:
            yield
            return
        try:
            from codecarbon import EmissionsTracker

            tracker = EmissionsTracker(
                project_name="ecollm-rag",
                measure_power_secs=1,
                save_to_file=False,
                logging_logger=None,
            )
            tracker.start()
            yield
            tracker.stop()
            self._codecarbon_emissions = tracker
        except Exception:
            yield
            self._codecarbon_emissions = None

    def codecarbon_wh(self) -> float:
        if self._codecarbon_emissions is None:
            return 0.0
        try:
            kwh = float(getattr(self._codecarbon_emissions, "final_emissions", 0) or 0)
            # CodeCarbon reports energy in kWh in some versions; check energy field
            energy = getattr(self._codecarbon_emissions, "_total_energy", None)
            if energy is not None:
                return float(energy) * 1000  # kWh -> Wh if needed
            return kwh * 1000 if kwh < 1 else kwh
        except Exception:
            return 0.0

    def estimate_from_tokens(
        self,
        input_tokens: int,
        output_tokens: int,
        model_tier: str,
        latency_ms: float,
        strategy: str = "",
    ) -> EnergyMetrics:
        total = input_tokens + output_tokens
        rate = ENERGY_WH_PER_1K_TOKENS.get(model_tier, ENERGY_WH_PER_1K_TOKENS["small"])
        energy_wh = (total / 1000.0) * rate
        co2_g = energy_wh * self._co2_factor
        cc_wh = self.codecarbon_wh()

        return EnergyMetrics(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total,
            latency_ms=latency_ms,
            energy_wh=energy_wh + cc_wh * 0.001,
            co2_g=co2_g,
            model_tier=model_tier,
            strategy=strategy,
            codecarbon_wh=cc_wh,
        )

    @staticmethod
    def compare_to_baseline(
        optimized: EnergyMetrics,
        baseline_tokens: int,
        baseline_energy_wh: float,
        baseline_latency_ms: float,
    ) -> EnergyMetrics:
        optimized.tokens_saved_vs_baseline = max(0, baseline_tokens - optimized.total_tokens)
        if baseline_energy_wh > 0:
            optimized.energy_saved_pct = (
                (baseline_energy_wh - optimized.energy_wh) / baseline_energy_wh
            ) * 100
        if baseline_latency_ms > 0:
            optimized.latency_saved_pct = (
                (baseline_latency_ms - optimized.latency_ms) / baseline_latency_ms
            ) * 100
        return optimized


def simulate_latency_ms(model_tier: str, total_tokens: int, rag_steps: int = 0) -> float:
    """Simulate realistic latency tiers for demo."""
    base = {"tiny": 12, "small": 35, "large": 120}[model_tier]
    per_token = {"tiny": 0.8, "small": 2.5, "large": 8.0}[model_tier]
    rag_penalty = rag_steps * {"tiny": 15, "small": 25, "large": 40}[model_tier]
    return base + total_tokens * per_token + rag_penalty

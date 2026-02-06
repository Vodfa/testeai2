from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass
class PredictionResult:
    probability_up: float
    should_buy: bool
    details: str


class MarketDirectionPredictor:
    """Heuristic predictor similar to technical-strategy style bots."""

    def __init__(self, buy_threshold: float = 0.62):
        self.buy_threshold = buy_threshold

    @staticmethod
    def _ema(values: Sequence[float], period: int) -> float:
        alpha = 2 / (period + 1)
        ema = float(values[0])
        for price in values[1:]:
            ema = (float(price) * alpha) + (ema * (1 - alpha))
        return ema

    @staticmethod
    def _rsi(values: Sequence[float], period: int = 14) -> float:
        deltas = [values[i] - values[i - 1] for i in range(1, len(values))]
        gains = [max(d, 0) for d in deltas]
        losses = [max(-d, 0) for d in deltas]
        if not gains and not losses:
            return 50.0

        g_slice = gains[-period:] if len(gains) >= period else gains
        l_slice = losses[-period:] if len(losses) >= period else losses
        avg_gain = sum(g_slice) / len(g_slice) if g_slice else 0
        avg_loss = sum(l_slice) / len(l_slice) if l_slice else 0
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def predict(self, closes: Sequence[float], volumes: Sequence[float]) -> PredictionResult:
        if len(closes) < 30:
            raise ValueError("São necessários pelo menos 30 candles para análise.")

        ema_fast = self._ema(closes[-20:], 9)
        ema_slow = self._ema(closes[-20:], 20)
        trend_score = 1 if ema_fast > ema_slow else 0

        rsi = self._rsi(closes[-30:], 14)
        rsi_score = 1 if 45 <= rsi <= 70 else 0

        vol_recent = volumes[-10:]
        vol_base = volumes[-30:]
        vol_mean_recent = sum(vol_recent) / len(vol_recent)
        vol_mean_base = sum(vol_base) / len(vol_base)
        volume_score = 1 if vol_mean_recent >= vol_mean_base else 0

        momentum = (closes[-1] - closes[-5]) / closes[-5]
        momentum_score = 1 if momentum > 0 else 0

        probability_up = (trend_score + rsi_score + volume_score + momentum_score) / 4
        should_buy = probability_up >= self.buy_threshold

        details = (
            f"EMA9={ema_fast:.2f} EMA20={ema_slow:.2f} | RSI={rsi:.2f} | "
            f"VolRec={vol_mean_recent:.2f} VolBase={vol_mean_base:.2f} | Momentum={momentum:.4f}"
        )

        return PredictionResult(probability_up=probability_up, should_buy=should_buy, details=details)

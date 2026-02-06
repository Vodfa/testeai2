from __future__ import annotations

from dataclasses import dataclass
from json import loads
from typing import Any, Iterable, List
from urllib.request import urlopen


DEFAULT_FREQTRADE_TRADES_URL = (
    "https://raw.githubusercontent.com/freqtrade/freqtrade/develop/"
    "tests/testdata/backtest_results/backtest-result.json"
)


@dataclass
class TradeMetric:
    profit_ratio: float


@dataclass
class FreqtradeBaseline:
    total_trades: int
    win_rate: float
    avg_profit_ratio: float
    expectancy: float
    market_bias: float


class FreqtradeDataError(RuntimeError):
    pass


class FreqtradeDataAnalyzer:
    def load_trades_from_github(self, url: str = DEFAULT_FREQTRADE_TRADES_URL) -> List[TradeMetric]:
        try:
            with urlopen(url, timeout=20) as response:
                payload = loads(response.read().decode("utf-8"))
        except Exception as exc:  # network/format errors
            raise FreqtradeDataError(f"Falha ao carregar dados do GitHub: {exc}") from exc

        return self._parse_payload(payload)

    def _parse_payload(self, payload: Any) -> List[TradeMetric]:
        raw_trades: Iterable[dict[str, Any]]
        if isinstance(payload, list):
            raw_trades = payload
        elif isinstance(payload, dict):
            if isinstance(payload.get("trades"), list):
                raw_trades = payload["trades"]
            elif isinstance(payload.get("results"), list):
                raw_trades = payload["results"]
            else:
                raise FreqtradeDataError("Formato de trades não reconhecido no payload Freqtrade.")
        else:
            raise FreqtradeDataError("Payload inválido de trades Freqtrade.")

        trades: List[TradeMetric] = []
        for item in raw_trades:
            if not isinstance(item, dict):
                continue
            profit = item.get("profit_ratio", item.get("profit_abs", 0.0))
            try:
                trades.append(TradeMetric(profit_ratio=float(profit)))
            except (TypeError, ValueError):
                continue

        if not trades:
            raise FreqtradeDataError("Nenhum trade válido encontrado para análise.")
        return trades

    def build_baseline(self, trades: List[TradeMetric]) -> FreqtradeBaseline:
        total = len(trades)
        wins = sum(1 for t in trades if t.profit_ratio > 0)
        win_rate = wins / total
        avg_profit = sum(t.profit_ratio for t in trades) / total

        avg_win = sum(t.profit_ratio for t in trades if t.profit_ratio > 0) / max(wins, 1)
        losses = total - wins
        avg_loss = sum(t.profit_ratio for t in trades if t.profit_ratio <= 0) / max(losses, 1)
        expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)

        market_bias = max(-0.15, min(0.15, ((win_rate - 0.5) * 0.4) + (expectancy * 2)))

        return FreqtradeBaseline(
            total_trades=total,
            win_rate=win_rate,
            avg_profit_ratio=avg_profit,
            expectancy=expectancy,
            market_bias=market_bias,
        )

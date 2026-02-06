from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, Optional

from app.core.market import BinanceMarketClient
from app.core.predictor import MarketDirectionPredictor


@dataclass
class BotConfig:
    symbol: str
    interval: str
    candle_limit: int
    buy_threshold: float
    poll_seconds: int
    trade_amount: float
    dry_run: bool
    max_runtime_minutes: int
    market_bias: float = 0.0


class TradingBotEngine:
    def __init__(
        self,
        config: BotConfig,
        log_callback: Callable[[str], None],
        trade_callback: Callable[[str, float, bool], None],
        market_client: Optional[BinanceMarketClient] = None,
    ):
        self.config = config
        self.log = log_callback
        self.trade_callback = trade_callback
        self.market_client = market_client or BinanceMarketClient()
        self.predictor = MarketDirectionPredictor(
            buy_threshold=config.buy_threshold,
            market_bias=config.market_bias,
        )
        self.started_at: Optional[datetime] = None
        self.running = False

    def start(self) -> None:
        self.started_at = datetime.now()
        self.running = True
        self.log("Bot iniciado.")

    def stop(self) -> None:
        self.running = False
        self.log("Bot parado.")

    def should_stop_by_time(self) -> bool:
        if self.config.max_runtime_minutes <= 0 or not self.started_at:
            return False
        return datetime.now() >= self.started_at + timedelta(minutes=self.config.max_runtime_minutes)

    def tick(self) -> None:
        if not self.running:
            return

        if self.should_stop_by_time():
            self.log("Tempo máximo atingido. Encerrando execução automaticamente.")
            self.stop()
            return

        candles = self.market_client.fetch_candles(
            symbol=self.config.symbol,
            interval=self.config.interval,
            limit=self.config.candle_limit,
        )
        closes = [c.close_price for c in candles]
        volumes = [c.volume for c in candles]
        pred = self.predictor.predict(closes, volumes)

        self.log(
            f"[{datetime.now().strftime('%H:%M:%S')}] Prob. alta={pred.probability_up:.2f} "
            f"(buy_threshold={self.config.buy_threshold:.2f}) | {pred.details}"
        )

        if pred.should_buy:
            self.trade_callback(self.config.symbol, self.config.trade_amount, self.config.dry_run)
        else:
            self.log("Sinal de compra não confirmado neste ciclo.")

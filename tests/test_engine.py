import unittest
from datetime import datetime, timedelta

from app.core.bot import BotConfig, TradingBotEngine


class DummyMarket:
    def fetch_candles(self, symbol, interval, limit):
        class C:
            def __init__(self, close_price, volume):
                self.close_price = close_price
                self.volume = volume

        return [C(100 + (i * 0.5), 1000 + i) for i in range(limit)]


class EngineTests(unittest.TestCase):
    def test_engine_stops_by_runtime_limit(self):
        logs = []
        trades = []
        cfg = BotConfig(
            symbol="BTCUSDT",
            interval="5m",
            candle_limit=60,
            buy_threshold=0.5,
            poll_seconds=5,
            trade_amount=10,
            dry_run=True,
            max_runtime_minutes=1,
        )

        engine = TradingBotEngine(cfg, logs.append, lambda s, a, d: trades.append((s, a, d)), market_client=DummyMarket())
        engine.start()
        engine.started_at = datetime.now() - timedelta(minutes=2)

        engine.tick()

        self.assertFalse(engine.running)
        self.assertTrue(any("Tempo máximo atingido" in line for line in logs))


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

from dataclasses import dataclass
from json import loads
from typing import List
from urllib.parse import urlencode
from urllib.request import urlopen


@dataclass
class Candle:
    open_time: int
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float


class BinanceMarketClient:
    """Simple client for Binance klines endpoint using Python stdlib."""

    BASE_URL = "https://api.binance.com/api/v3/klines"

    def fetch_candles(self, symbol: str, interval: str, limit: int = 200) -> List[Candle]:
        params = urlencode({"symbol": symbol.upper(), "interval": interval, "limit": limit})
        url = f"{self.BASE_URL}?{params}"
        with urlopen(url, timeout=15) as response:
            status = getattr(response, "status", 200)
            if status >= 400:
                raise RuntimeError(f"Falha ao buscar candles. HTTP {status}")
            data = loads(response.read().decode("utf-8"))

        candles: List[Candle] = []
        for row in data:
            candles.append(
                Candle(
                    open_time=int(row[0]),
                    open_price=float(row[1]),
                    high_price=float(row[2]),
                    low_price=float(row[3]),
                    close_price=float(row[4]),
                    volume=float(row[5]),
                )
            )
        return candles

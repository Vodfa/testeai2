import json
import unittest
from unittest.mock import patch

from app.core.market import BinanceMarketClient


class FakeResponse:
    def __init__(self, payload, status=200):
        self._payload = payload
        self.status = status

    def read(self):
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class MarketClientTests(unittest.TestCase):
    @patch("app.core.market.urlopen")
    def test_fetch_candles_parses_payload(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse(
            [
                [1710000000, "100.0", "110.0", "99.0", "108.5", "1500.0"],
                [1710000300, "108.5", "112.0", "107.0", "111.2", "1700.5"],
            ]
        )

        candles = BinanceMarketClient().fetch_candles("btcusdt", "5m", limit=2)

        self.assertEqual(2, len(candles))
        self.assertEqual(1710000000, candles[0].open_time)
        self.assertEqual(111.2, candles[1].close_price)


if __name__ == "__main__":
    unittest.main()

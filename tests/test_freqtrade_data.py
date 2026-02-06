import unittest

from app.core.freqtrade_data import FreqtradeDataAnalyzer


class FreqtradeDataTests(unittest.TestCase):
    def test_parse_payload_and_build_baseline(self):
        analyzer = FreqtradeDataAnalyzer()
        trades = analyzer._parse_payload(
            {
                "trades": [
                    {"profit_ratio": 0.03},
                    {"profit_ratio": -0.01},
                    {"profit_ratio": 0.02},
                ]
            }
        )
        baseline = analyzer.build_baseline(trades)

        self.assertEqual(3, baseline.total_trades)
        self.assertAlmostEqual(2 / 3, baseline.win_rate)
        self.assertTrue(-0.15 <= baseline.market_bias <= 0.15)


if __name__ == "__main__":
    unittest.main()

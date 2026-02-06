import unittest

from app.core.predictor import MarketDirectionPredictor


class PredictorTests(unittest.TestCase):
    def test_predictor_detects_uptrend_buy_signal(self):
        predictor = MarketDirectionPredictor(buy_threshold=0.5)
        closes = [100 + (i * 0.5) for i in range(40)]
        volumes = [1000 + (i * 10) for i in range(40)]

        result = predictor.predict(closes, volumes)

        self.assertGreaterEqual(result.probability_up, 0.5)
        self.assertTrue(result.should_buy)

    def test_predictor_requires_enough_candles(self):
        predictor = MarketDirectionPredictor()
        closes = [1.0] * 10
        volumes = [1.0] * 10

        with self.assertRaises(ValueError):
            predictor.predict(closes, volumes)


if __name__ == "__main__":
    unittest.main()

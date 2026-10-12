import unittest
from datetime import date

from tarot.daily import daily_spread
from tarot.spread_image import render_spread


class SpreadImageTest(unittest.TestCase):
    def test_render_is_jpeg(self) -> None:
        spread = daily_spread(1, date(2026, 10, 12))
        payload = render_spread(spread)
        self.assertTrue(payload.startswith(b"\xff\xd8"))
        self.assertGreater(len(payload), 50_000)
        again = render_spread(spread)
        self.assertEqual(payload, again)


if __name__ == "__main__":
    unittest.main()

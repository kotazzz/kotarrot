import unittest
from datetime import date

from tarot.daily import daily_result, daily_spread, pick_from_seed, seed_for
from tarot.deck import THEME_IDS, load_cards

KNOWN_SEED = "f6d5a273cc568135c41f8e023f4beb735587d854c347c46aa096eca05364c2f9"


class DailyResultTest(unittest.TestCase):
    def test_seed_is_stable(self) -> None:
        self.assertEqual(seed_for(1, date(2026, 10, 12)), KNOWN_SEED)

    def test_same_user_same_day_is_same_result(self) -> None:
        first = daily_result(7, date(2026, 10, 12), tz_name="Europe/Minsk")
        second = daily_result(7, date(2026, 10, 12), tz_name="Europe/Minsk")
        self.assertEqual(first, second)
        self.assertEqual(first.to_dict(), second.to_dict())

    def test_result_depends_on_user_and_date(self) -> None:
        base = daily_result(7, date(2026, 10, 12))
        other_user = daily_result(8, date(2026, 10, 12))
        other_day = daily_result(7, date(2026, 10, 13))
        self.assertNotEqual(base.seed, other_user.seed)
        self.assertNotEqual(base.seed, other_day.seed)
        self.assertNotEqual(
            (base.card_id, base.orientation),
            (other_user.card_id, other_user.orientation),
        )
        self.assertNotEqual(
            (base.card_id, base.orientation),
            (other_day.card_id, other_day.orientation),
        )

    def test_known_draw(self) -> None:
        result = daily_result(1, date(2026, 10, 12))
        index, orientation = pick_from_seed(KNOWN_SEED, 78)
        self.assertEqual(index, 47)
        self.assertEqual(orientation, "upright")
        self.assertEqual(result.card_index, 47)
        self.assertEqual(result.orientation, "upright")
        self.assertEqual(result.card_id, "cups-12-knight")
        card = load_cards()[47]
        self.assertEqual(result.general, card["general"]["upright"])
        for theme in THEME_IDS:
            self.assertEqual(result.themes[theme], card["themes"][theme]["upright"])


class DailySpreadTest(unittest.TestCase):
    def test_same_user_same_day_is_same_spread(self) -> None:
        first = daily_spread(7, date(2026, 10, 12), tz_name="Europe/Minsk")
        second = daily_spread(7, date(2026, 10, 12), tz_name="Europe/Minsk")
        self.assertEqual(first, second)
        self.assertEqual(len(first.cards), 3)
        self.assertEqual(len({item.card_id for item in first.cards}), 3)

    def test_spread_depends_on_user_and_date(self) -> None:
        base = daily_spread(7, date(2026, 10, 12))
        other_user = daily_spread(8, date(2026, 10, 12))
        other_day = daily_spread(7, date(2026, 10, 13))
        base_key = tuple((item.card_id, item.orientation) for item in base.cards)
        self.assertNotEqual(
            base_key,
            tuple((item.card_id, item.orientation) for item in other_user.cards),
        )
        self.assertNotEqual(
            base_key,
            tuple((item.card_id, item.orientation) for item in other_day.cards),
        )

    def test_known_first_card_stays_in_spread(self) -> None:
        spread = daily_spread(1, date(2026, 10, 12))
        first = spread.cards[0]
        self.assertEqual(first.position, "Прошлое")
        self.assertEqual(first.card_id, "cups-12-knight")
        self.assertEqual(first.orientation, "upright")
        self.assertEqual([item.position for item in spread.cards], ["Прошлое", "Настоящее", "Будущее"])


if __name__ == "__main__":
    unittest.main()

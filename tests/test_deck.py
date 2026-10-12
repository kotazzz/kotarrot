import unittest

from tarot.deck import THEME_IDS, load_cards, load_deck


class DeckTest(unittest.TestCase):
    def test_counts(self) -> None:
        payload = load_deck()
        cards = load_cards()
        self.assertEqual(len(cards), 78)
        self.assertEqual(payload["deck"]["theme_reading_count"], 780)
        texts: list[str] = []
        for card in cards:
            for orientation in ("upright", "reversed"):
                texts.append(card["general"][orientation])
                for theme in THEME_IDS:
                    texts.append(card["themes"][theme][orientation])
        self.assertEqual(len(texts), 936)
        self.assertEqual(len(set(texts)), 936)

    def test_images_are_jpeg_paths(self) -> None:
        for card in load_cards():
            self.assertTrue(card["image"].endswith(".jpg"))
            self.assertTrue(card["image_url"].startswith("https://upload.wikimedia.org/"))


if __name__ == "__main__":
    unittest.main()

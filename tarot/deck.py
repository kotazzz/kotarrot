from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECK_PATH = ROOT / "data" / "cards.json"

THEME_IDS = ("love", "career", "self", "choice", "future")

THEME_TITLES = {
    "love": "Любовь и отношения",
    "career": "Карьера, работа и финансы",
    "self": "Самопознание и личностный рост",
    "choice": "Выбор и принятие решений",
    "future": "Будущее и прогнозы",
}


@lru_cache(maxsize=1)
def load_deck() -> dict:
    if not DECK_PATH.is_file():
        raise FileNotFoundError(
            "Нет файла data/cards.json. Сначала выполни: python -m deckgen.build"
        )
    with DECK_PATH.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    cards = payload.get("cards")
    if not isinstance(cards, list) or len(cards) != 78:
        raise ValueError("В колоде должно быть 78 карт")
    ordered = sorted(cards, key=lambda item: item["index"])
    indexes = [item["index"] for item in ordered]
    if indexes != list(range(78)):
        raise ValueError("Индексы карт должны идти от 0 до 77 без пропусков")
    payload["cards"] = ordered
    return payload


def load_cards() -> list[dict]:
    return load_deck()["cards"]

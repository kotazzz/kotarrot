from __future__ import annotations

THEME_IDS = ("love", "career", "self", "choice", "future")

THEME_TITLES = {
    "love": "Любовь и отношения",
    "career": "Карьера, работа и финансы",
    "self": "Самопознание и личностный рост",
    "choice": "Выбор и принятие решений",
    "future": "Будущее и прогнозы",
}

MIN_TEXT = 80


def _side(upright: str, reversed_: str, label: str) -> dict[str, str]:
    sides = {"upright": upright.strip(), "reversed": reversed_.strip()}
    for key, value in sides.items():
        if len(value) < MIN_TEXT:
            raise ValueError(f"{label} {key}: короткий текст ({len(value)})")
    return sides


def card(
    index: int,
    slug: str,
    name: str,
    name_en: str,
    *,
    arcana: str,
    number: int | None,
    suit: str | None,
    rank: str | None,
    source_file: str,
    source_url: str,
    keywords_up: tuple[str, ...],
    keywords_rev: tuple[str, ...],
    general: tuple[str, str],
    love: tuple[str, str],
    career: tuple[str, str],
    growth: tuple[str, str],
    choice: tuple[str, str],
    future: tuple[str, str],
    element: str | None = None,
) -> dict:
    themes = {
        "love": _side(*love, f"{slug} love"),
        "career": _side(*career, f"{slug} career"),
        "self": _side(*growth, f"{slug} self"),
        "choice": _side(*choice, f"{slug} choice"),
        "future": _side(*future, f"{slug} future"),
    }
    return {
        "index": index,
        "id": slug,
        "arcana": arcana,
        "suit": suit,
        "rank": rank,
        "number": number,
        "element": element,
        "name": name,
        "name_en": name_en,
        "image": f"images/{slug}.jpg",
        "image_source": source_file,
        "image_url": source_url,
        "keywords": {
            "upright": list(keywords_up),
            "reversed": list(keywords_rev),
        },
        "general": _side(*general, f"{slug} general"),
        "themes": themes,
    }

from __future__ import annotations

import json
from pathlib import Path

from deckgen.cups import CARDS as CUPS
from deckgen.major import CARDS as MAJOR
from deckgen.model import THEME_IDS, THEME_TITLES
from deckgen.pentacles import CARDS as PENTACLES
from deckgen.swords import CARDS as SWORDS
from deckgen.wands import CARDS as WANDS

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "cards.json"
MARKDOWN_PATH = ROOT / "data" / "cards.md"

ORIENTATIONS = ("upright", "reversed")
ORIENTATION_TITLES = {
    "upright": "Прямое положение",
    "reversed": "Перевёрнутое положение",
}


def collect_cards() -> list[dict]:
    cards = [*MAJOR, *WANDS, *CUPS, *SWORDS, *PENTACLES]
    if len(cards) != 78:
        raise SystemExit(f"Ожидалось 78 карт, собрано {len(cards)}")
    indexes = [item["index"] for item in cards]
    if indexes != list(range(78)):
        raise SystemExit(f"Индексы идут не по порядку: {indexes}")
    ids = [item["id"] for item in cards]
    if len(set(ids)) != 78:
        raise SystemExit("Есть повторяющиеся id карт")
    texts: list[str] = []
    for item in cards:
        if not str(item["image"]).endswith(".jpg"):
            raise SystemExit(f"Нужен jpg: {item['id']}")
        if not str(item["image_url"]).startswith("https://upload.wikimedia.org/"):
            raise SystemExit(f"Нет адреса картинки: {item['id']}")
        for orientation in ORIENTATIONS:
            texts.append(item["general"][orientation])
        for theme in THEME_IDS:
            if set(item["themes"][theme]) != set(ORIENTATIONS):
                raise SystemExit(f"Битая тема {theme} у {item['id']}")
            for orientation in ORIENTATIONS:
                texts.append(item["themes"][theme][orientation])
    if len(texts) != 78 * 12:
        raise SystemExit(f"Ожидалось 936 текстов, собрано {len(texts)}")
    if len(set(texts)) != len(texts):
        seen: set[str] = set()
        for text in texts:
            if text in seen:
                raise SystemExit(f"Повтор толкования: {text}")
            seen.add(text)
    return cards


def deck_payload(cards: list[dict]) -> dict:
    return {
        "deck": {
            "id": "rider-waite-smith",
            "name": "Таро Райдера — Уэйта",
            "language": "ru",
            "card_count": 78,
            "reading_count": 78 * 12,
            "theme_reading_count": 78 * 10,
            "images": {
                "format": "jpeg",
                "source": "https://commons.wikimedia.org/wiki/Category:Rider-Waite-Smith_tarot_deck_(TaionWC)",
                "license": "Public domain",
                "note": "Скан Pam-A колоды 1910 года. Рисунок Памелы Колман Смит.",
            },
            "texts": "Оригинальные толкования в традиции Райдера — Уэйта для сборки ответа на расклад.",
        },
        "themes": [
            {"id": theme, "title": THEME_TITLES[theme]}
            for theme in THEME_IDS
        ],
        "cards": cards,
    }


def render_markdown(payload: dict) -> str:
    lines = [
        f"# {payload['deck']['name']}",
        "",
        "78 карт. У каждой — общее значение и пять тем, в прямом и перевёрнутом положении.",
        "",
    ]
    titles = {item["id"]: item["title"] for item in payload["themes"]}
    for item in payload["cards"]:
        lines.append(f"## {item['index']:02d}. {item['name']}")
        lines.append("")
        lines.append(f"Картинка: `{item['image']}`")
        lines.append("")
        lines.append("### Общее значение")
        lines.append("")
        for orientation in ORIENTATIONS:
            lines.append(f"**{ORIENTATION_TITLES[orientation]}.** {item['general'][orientation]}")
            lines.append("")
        for theme in THEME_IDS:
            lines.append(f"### {titles[theme]}")
            lines.append("")
            for orientation in ORIENTATIONS:
                text = item["themes"][theme][orientation]
                lines.append(f"**{ORIENTATION_TITLES[orientation]}.** {text}")
                lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    cards = collect_cards()
    payload = deck_payload(cards)
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    MARKDOWN_PATH.write_text(render_markdown(payload), encoding="utf-8")
    print(f"cards=78 texts={78 * 12} json={DATA_PATH.name} md={MARKDOWN_PATH.name}")


if __name__ == "__main__":
    main()

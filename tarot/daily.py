from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from datetime import date, datetime
from zoneinfo import ZoneInfo

from tarot.deck import THEME_IDS, load_cards

DEFAULT_TIMEZONE = "Europe/Minsk"

MONTHS = (
    "января",
    "февраля",
    "марта",
    "апреля",
    "мая",
    "июня",
    "июля",
    "августа",
    "сентября",
    "октября",
    "ноября",
    "декабря",
)


@dataclass(frozen=True)
class DailyResult:
    user_id: str
    on: date
    timezone: str
    seed: str
    card_index: int
    card_id: str
    card_name: str
    orientation: str
    general: str
    themes: dict[str, str]
    image: str

    @property
    def date_label(self) -> str:
        return f"{self.on.day} {MONTHS[self.on.month - 1]}"

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "date": self.on.isoformat(),
            "timezone": self.timezone,
            "seed": self.seed,
            "orientation": self.orientation,
            "card": {
                "index": self.card_index,
                "id": self.card_id,
                "name": self.card_name,
                "image": self.image,
            },
            "general": self.general,
            "themes": dict(self.themes),
        }


def timezone_name() -> str:
    value = os.getenv("DAILY_TIMEZONE", DEFAULT_TIMEZONE).strip()
    return value or DEFAULT_TIMEZONE


def today(tz_name: str | None = None) -> date:
    zone = ZoneInfo(tz_name or timezone_name())
    return datetime.now(zone).date()


def seed_for(user_id: int | str, on: date) -> str:
    raw = f"{user_id}:{on.isoformat()}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def pick_from_seed(seed_hex: str, size: int) -> tuple[int, str]:
    digest = bytes.fromhex(seed_hex)
    index = int.from_bytes(digest[:8], "big") % size
    orientation = "upright" if digest[8] % 2 == 0 else "reversed"
    return index, orientation


SPREAD_POSITIONS = (
    ("past", "Прошлое"),
    ("present", "Настоящее"),
    ("future", "Будущее"),
)


def pick_spread(seed_hex: str, size: int, count: int = 3) -> list[tuple[int, str]]:
    if count > size:
        raise ValueError("В колоде меньше карт, чем позиций в раскладе")
    first_index, first_orientation = pick_from_seed(seed_hex, size)
    chosen = [(first_index, first_orientation)]
    used = {first_index}
    stream = bytearray(bytes.fromhex(seed_hex))
    cursor = 9
    steps = 0
    while len(chosen) < count:
        steps += 1
        if steps > size * 4:
            raise RuntimeError("Не удалось выбрать разные карты расклада")
        if cursor + 9 > len(stream):
            stream.extend(hashlib.sha256(bytes(stream)).digest())
        index = int.from_bytes(stream[cursor:cursor + 8], "big") % size
        orientation = "upright" if stream[cursor + 8] % 2 == 0 else "reversed"
        cursor += 9
        if index in used:
            continue
        used.add(index)
        chosen.append((index, orientation))
    return chosen


def daily_result(
    user_id: int | str,
    on: date | None = None,
    tz_name: str | None = None,
) -> DailyResult:
    zone = tz_name or timezone_name()
    day = today(zone) if on is None else on
    cards = load_cards()
    seed = seed_for(user_id, day)
    index, orientation = pick_from_seed(seed, len(cards))
    chosen = cards[index]
    themes = {
        theme: chosen["themes"][theme][orientation]
        for theme in THEME_IDS
    }
    return DailyResult(
        user_id=str(user_id),
        on=day,
        timezone=zone,
        seed=seed,
        card_index=index,
        card_id=chosen["id"],
        card_name=chosen["name"],
        orientation=orientation,
        general=chosen["general"][orientation],
        themes=themes,
        image=chosen["image"],
    )


@dataclass(frozen=True)
class SpreadCard:
    position_id: str
    position: str
    card_index: int
    card_id: str
    card_name: str
    orientation: str
    general: str
    image: str


@dataclass(frozen=True)
class DailySpread:
    user_id: str
    on: date
    timezone: str
    seed: str
    cards: tuple[SpreadCard, ...]

    @property
    def date_label(self) -> str:
        return f"{self.on.day} {MONTHS[self.on.month - 1]}"

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "date": self.on.isoformat(),
            "timezone": self.timezone,
            "seed": self.seed,
            "cards": [
                {
                    "position_id": item.position_id,
                    "position": item.position,
                    "index": item.card_index,
                    "id": item.card_id,
                    "name": item.card_name,
                    "orientation": item.orientation,
                    "general": item.general,
                    "image": item.image,
                }
                for item in self.cards
            ],
        }


def daily_spread(
    user_id: int | str,
    on: date | None = None,
    tz_name: str | None = None,
) -> DailySpread:
    zone = tz_name or timezone_name()
    day = today(zone) if on is None else on
    cards = load_cards()
    seed = seed_for(user_id, day)
    picks = pick_spread(seed, len(cards), len(SPREAD_POSITIONS))
    drawn: list[SpreadCard] = []
    for (position_id, position), (index, orientation) in zip(SPREAD_POSITIONS, picks):
        chosen = cards[index]
        drawn.append(
            SpreadCard(
                position_id=position_id,
                position=position,
                card_index=index,
                card_id=chosen["id"],
                card_name=chosen["name"],
                orientation=orientation,
                general=chosen["general"][orientation],
                image=chosen["image"],
            )
        )
    return DailySpread(
        user_id=str(user_id),
        on=day,
        timezone=zone,
        seed=seed,
        cards=tuple(drawn),
    )

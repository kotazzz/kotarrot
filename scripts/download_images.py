from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECK_PATH = ROOT / "data" / "cards.json"
USER_AGENT = "tarotbot/1.0 (personal study archive of public-domain RWS scans; sequential)"
MIN_BYTES = 50_000
PAUSE_SECONDS = 1.5


def _download(url: str, destination: Path) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.is_file() and destination.stat().st_size >= MIN_BYTES:
        return f"skip {destination.name}"
    delay = PAUSE_SECONDS
    last_error = "неизвестная ошибка"
    for _ in range(6):
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                payload = response.read()
        except urllib.error.HTTPError as exc:
            last_error = f"HTTP {exc.code}"
            if exc.code != 429:
                raise
            time.sleep(delay)
            delay = min(delay * 2, 60)
            continue
        if len(payload) < MIN_BYTES or not payload.startswith(b"\xff\xd8"):
            raise RuntimeError(f"Плохой файл {destination.name}: {len(payload)} байт")
        destination.write_bytes(payload)
        return f"saved {destination.name} {len(payload)}"
    raise RuntimeError(last_error)


def main() -> None:
    deck = json.loads(DECK_PATH.read_text(encoding="utf-8"))
    jobs = [(card["image_url"], ROOT / card["image"]) for card in deck["cards"]]
    errors: list[str] = []
    for url, path in jobs:
        try:
            print(_download(url, path), flush=True)
        except Exception as exc:
            errors.append(f"{path.name}: {exc}")
            print(f"fail {path.name}: {exc}", flush=True)
        time.sleep(PAUSE_SECONDS)
    if errors:
        raise SystemExit(f"Не скачалось: {len(errors)}")
    print(f"images={len(jobs)}")


if __name__ == "__main__":
    main()

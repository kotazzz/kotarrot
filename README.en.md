# kotarrot

[Русский](README.md)

A Telegram bot for the Rider–Waite–Smith deck. The “Сделать расклад” button builds one image with three cards: past, present, and future. Each card has its reading underneath. A reversed card is drawn upside down.

The same person gets the same spread for the whole day. Nothing is stored: the cards are derived from the account id and the date. A new day starts at midnight. The timezone is `DAILY_TIMEZONE`, `Europe/Minsk` by default.

## Deck

`data/cards.json` and `data/cards.md` hold all 78 cards. Each card has a general meaning and five themes, upright and reversed: love, career and money, self-knowledge, choices, and forecast. That is 936 texts.

The readings are original and follow this deck’s tradition. The files in `images/` are a public-domain Pam-A scan from 1910, taken from [Wikimedia Commons](https://commons.wikimedia.org/wiki/Category:Rider-Waite-Smith_tarot_deck_(TaionWC)).

## Run

You need Python 3.11+ and a token from [@BotFather](https://t.me/BotFather).

```text
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m bot
```

Put `BOT_TOKEN` in `.env`. That file stays on your machine and is not committed. `.env.example` lists the variables.

On Windows, activate the environment with `.venv\Scripts\activate` and copy the example with `copy .env.example .env`.

Bot commands: `/start`, `/info`, `/help`.

If you edit the texts in `deckgen/`, rebuild the deck:

```text
python -m deckgen.build
```

If `images/` is empty, download the cards:

```text
python scripts/download_images.py
```

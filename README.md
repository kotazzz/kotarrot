# kotarrot

[English](README.en.md)

Telegram-бот с колодой Райдера — Уэйта. По кнопке «Сделать расклад» собирает картинку из трёх карт: прошлое, настоящее и будущее. Под каждой картой её значение. Перевёрнутая карта на картинке перевёрнута.

Один и тот же человек в одни сутки получает один и тот же расклад. Считать заново не нужно: карты выводятся из учётной записи и даты. Новые сутки начинаются в полночь. Часовой пояс задаётся в `DAILY_TIMEZONE`, по умолчанию `Europe/Minsk`.

## Колода

В `data/cards.json` и `data/cards.md` — 78 карт. У каждой общее значение и пять тем, в прямом и перевёрнутом положении: любовь, работа и деньги, самопознание, выбор, прогноз. Всего 936 текстов.

Тексты написаны заново, в традиции этой колоды. Картинки в `images/` — свободный скан Pam-A 1910 года с [Wikimedia Commons](https://commons.wikimedia.org/wiki/Category:Rider-Waite-Smith_tarot_deck_(TaionWC)).

## Запуск

Нужны Python 3.11+ и токен от [@BotFather](https://t.me/BotFather).

```text
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m bot
```

В `.env` впиши `BOT_TOKEN`. Файл `.env` локальный, в репозиторий он не коммитится. Образец переменных — `.env.example`.

На Linux и macOS вместо `copy` используй `cp .env.example .env`, окружение активируется через `source .venv/bin/activate`.

Команды бота: `/start`, `/info`, `/help`.

Если меняешь тексты в `deckgen/`, заново собери колоду:

```text
python -m deckgen.build
```

Картинки, если их нет в `images/`, скачиваются так:

```text
python scripts/download_images.py
```

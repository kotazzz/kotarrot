"""Запуск из корня проекта: python -m bot"""

import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from dotenv import load_dotenv

from tarot.daily import daily_spread, timezone_name
from tarot.deck import ROOT, load_cards
from tarot.spread_image import render_spread

load_dotenv(ROOT / ".env")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("tarotbot")

router = Router()


def _token() -> str:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        print("Укажи BOT_TOKEN в файле .env", file=sys.stderr)
        raise SystemExit(1)
    return token


def spread_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Сделать расклад", callback_data="spread")]
        ]
    )


def _caption(date_label: str) -> str:
    return f"Расклад на {date_label}. До конца этих суток он для тебя не изменится."


async def _send_spread(message: Message, user_id: int) -> None:
    spread = daily_spread(user_id)
    log.info(
        "spread user=%s cards=%s",
        user_id,
        ",".join(f"{item.card_id}:{item.orientation}" for item in spread.cards),
    )
    payload = render_spread(spread)
    photo = BufferedInputFile(payload, filename="spread.jpg")
    await message.answer_photo(
        photo,
        caption=_caption(spread.date_label),
        reply_markup=spread_keyboard(),
    )


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет. Нажми кнопку — соберу три карты: прошлое, настоящее и будущее.\n\n"
        "Для тебя этот расклад один на сутки.",
        reply_markup=spread_keyboard(),
    )


@router.message(Command("info"))
async def cmd_info(message: Message) -> None:
    await message.answer(
        "Колода Райдера — Уэйта: 78 карт.\n"
        "Расклад — три карты: прошлое, настоящее и будущее. "
        "Под каждой — карта и её значение.\n\n"
        "Карты считаются из твоей учётной записи и даты. "
        "Повтор в те же сутки даёт тот же расклад.\n"
        f"Новые сутки начинаются в полночь ({timezone_name()}).",
        reply_markup=spread_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "/start — начать\n"
        "/info — о колоде и о раскладе\n"
        "/help — список команд\n\n"
        "Кнопка «Сделать расклад» выкладывает три карты на сегодня.",
        reply_markup=spread_keyboard(),
    )


@router.callback_query(F.data == "spread")
async def on_spread(query: CallbackQuery) -> None:
    user = query.from_user
    if user is None or not isinstance(query.message, Message):
        await query.answer("Не вижу, кто нажал кнопку")
        return
    await query.answer()
    await _send_spread(query.message, user.id)


async def main() -> None:
    load_cards()
    bot = Bot(token=_token())
    dispatcher = Dispatcher()
    dispatcher.include_router(router)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

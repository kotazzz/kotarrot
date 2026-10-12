from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from tarot.daily import DailySpread
from tarot.deck import ROOT

CANVAS_WIDTH = 1800
MARGIN = 56
COLUMN_GAP = 36
CARD_HEIGHT = 760
BACKGROUND = (32, 24, 20)
TEXT = (246, 239, 230)
GOLD = (214, 178, 112)
MUTED = (196, 164, 132)
LINE = (92, 68, 48)

FONT_CANDIDATES = (
    Path(r"C:\Windows\Fonts\arial.ttf"),
    Path(r"C:\Windows\Fonts\segoeui.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
)
BOLD_CANDIDATES = (
    Path(r"C:\Windows\Fonts\arialbd.ttf"),
    Path(r"C:\Windows\Fonts\segoeuib.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
)


def _font_path(candidates: tuple[Path, ...]) -> Path:
    for path in candidates:
        if path.is_file():
            return path
    raise FileNotFoundError("Не найден шрифт с кириллицей для картинки расклада")


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = _font_path(BOLD_CANDIDATES if bold else FONT_CANDIDATES)
    return ImageFont.truetype(str(path), size=size)


def _wrap(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        current = ""
        for word in words:
            trial = word if not current else f"{current} {word}"
            if font.getlength(trial) <= max_width:
                current = trial
                continue
            if current:
                lines.append(current)
            current = word
        if current:
            lines.append(current)
    return lines or [""]


def _orientation_label(orientation: str) -> str:
    if orientation == "upright":
        return "прямое положение"
    return "перевёрнутое положение"


def _load_card(path: Path, height: int, reversed_card: bool) -> Image.Image:
    with Image.open(path) as source:
        card = source.convert("RGB")
    width = max(1, round(card.width * height / card.height))
    card = card.resize((width, height), Image.Resampling.LANCZOS)
    if reversed_card:
        card = card.transpose(Image.Transpose.ROTATE_180)
    return card


def render_spread(spread: DailySpread, root: Path | None = None) -> bytes:
    base = root or ROOT
    title_font = _font(58, bold=True)
    position_font = _font(40, bold=True)
    name_font = _font(36, bold=True)
    note_font = _font(28)
    body_font = _font(32)
    line_gap = 10

    column_width = (CANVAS_WIDTH - MARGIN * 2 - COLUMN_GAP * (len(spread.cards) - 1)) // len(spread.cards)
    text_width = column_width - 8
    columns: list[dict] = []
    for item in spread.cards:
        card = _load_card(base / item.image, CARD_HEIGHT, item.orientation == "reversed")
        name_lines = _wrap(item.card_name, name_font, text_width)
        body_lines = _wrap(item.general, body_font, text_width)
        columns.append(
            {
                "item": item,
                "card": card,
                "name_lines": name_lines,
                "body_lines": body_lines,
            }
        )

    header_height = 150
    text_heights = []
    for column in columns:
        text_height = (
            52
            + CARD_HEIGHT
            + 28
            + len(column["name_lines"]) * 46
            + 40
            + len(column["body_lines"]) * (32 + line_gap)
        )
        text_heights.append(text_height)
    height = header_height + max(text_heights) + MARGIN

    canvas = Image.new("RGB", (CANVAS_WIDTH, height), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    title = f"Расклад на {spread.date_label}"
    title_width = title_font.getlength(title)
    draw.text(((CANVAS_WIDTH - title_width) / 2, 42), title, font=title_font, fill=TEXT)
    draw.line((MARGIN, 124, CANVAS_WIDTH - MARGIN, 124), fill=LINE, width=2)

    x = MARGIN
    for column in columns:
        item = column["item"]
        card = column["card"]
        y = header_height
        position_width = position_font.getlength(item.position)
        draw.text((x + (column_width - position_width) / 2, y), item.position, font=position_font, fill=GOLD)
        y += 58
        card_x = x + (column_width - card.width) // 2
        frame = (card_x - 4, y - 4, card_x + card.width + 4, y + card.height + 4)
        draw.rectangle(frame, outline=GOLD, width=3)
        canvas.paste(card, (card_x, y))
        y += card.height + 24
        for line in column["name_lines"]:
            line_width = name_font.getlength(line)
            draw.text((x + (column_width - line_width) / 2, y), line, font=name_font, fill=TEXT)
            y += 46
        note = _orientation_label(item.orientation)
        note_width = note_font.getlength(note)
        draw.text((x + (column_width - note_width) / 2, y), note, font=note_font, fill=MUTED)
        y += 48
        for line in column["body_lines"]:
            draw.text((x, y), line, font=body_font, fill=TEXT)
            y += 32 + line_gap
        x += column_width + COLUMN_GAP

    buffer = BytesIO()
    canvas.save(buffer, format="JPEG", quality=90)
    return buffer.getvalue()

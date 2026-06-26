from datetime import datetime, timedelta

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import SERVICES, TIME_SLOTS
from database import get_booked_slots


def services_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=desc, callback_data=f"svc_{key}")]
            for key, desc in SERVICES.items()
        ]
    )


def date_kb():
    today = datetime.now()
    buttons = []
    for i in range(7):
        d = today + timedelta(days=i)
        label = d.strftime("%d.%m (%a)")
        cb = f"date_{d.strftime('%d.%m.%Y')}"
        buttons.append([InlineKeyboardButton(text=label, callback_data=cb)])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def time_kb(date):
    booked = get_booked_slots(date)
    buttons, row = [], []
    for i, slot in enumerate(TIME_SLOTS, 1):
        if slot in booked:
            row.append(InlineKeyboardButton(text=f" {slot} ", callback_data="disabled"))
        else:
            row.append(InlineKeyboardButton(text=slot, callback_data=f"time_{slot}"))
        if i % 3 == 0:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def review_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=n, callback_data=f"rate_{n}")
                for n in ("1", "2", "3", "4", "5")
            ]
        ]
    )


def my_bookings_kb(appointments):
    buttons = []
    for a in appointments:
        label = f"{a['date']} {a['time']} — {a['service'][:20]}"
        buttons.append([InlineKeyboardButton(text=label, callback_data=f"cancel_{a['id']}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Подтвердить", callback_data="confirm_yes")],
            [InlineKeyboardButton(text="Назад", callback_data="confirm_no")],
        ]
    )


def confirm_cancel_kb(aid):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Да, отменить", callback_data=f"cnf_{aid}")],
            [InlineKeyboardButton(text="Нет, оставить", callback_data="keep")],
        ]
    )

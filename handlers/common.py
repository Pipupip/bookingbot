from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from config import SERVICES
from database import add_user, get_user_appointments
from keyboards.menu import main_kb
from keyboards.inline import my_bookings_kb, confirm_cancel_kb, review_kb
from states.booking import CancelStates, ReviewStates

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    add_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    await message.answer(
        "Добро пожаловать в автосервис!\n\n"
        "Нажмите <b>Записаться онлайн</b> чтобы выбрать удобное время.\n\n"
        "Мы работаем Пн–Сб с 09:00 до 19:00.",
        reply_markup=main_kb(),
    )


@router.message(F.text == "Услуги и цены")
async def show_services(message: Message):
    lines = ["<b>Наши услуги:</b>\n"]
    for desc in SERVICES.values():
        lines.append(f"• {desc}")
    await message.answer("\n".join(lines))


@router.message(F.text == "О нас")
async def show_about(message: Message):
    await message.answer(
        "Автосервис «Профи» — более 10 лет на рынке.\n"
        "Современное оборудование, гарантия на все виды работ.\n"
        "Более 5 000 довольных клиентов!"
    )


@router.message(F.text == "Контакты")
async def show_contacts(message: Message):
    await message.answer(
        "📍 Адрес: г. Москва, ул. Автомобильная, д. 15\n"
        " Телефон: +7 (999) 123-45-67\n"
        " График: Пн–Сб 09:00–19:00\n"
        " Email: info@prof-auto.ru"
    )


@router.message(F.text == "Мои записи")
async def my_bookings(message: Message):
    apps = get_user_appointments(message.from_user.id)
    if not apps:
        await message.answer("У вас нет активных записей.")
        return
    text = "<b>Ваши записи:</b>\n\n"
    for a in apps:
        text += f" {a['service']}\n   {a['date']} в {a['time']}\n\n"
    text += "Выберите запись для отмены:"
    await message.answer(text, reply_markup=my_bookings_kb(apps))


@router.callback_query(F.data.startswith("cancel_"))
async def select_cancel(callback: CallbackQuery):
    aid = int(callback.data.replace("cancel_", ""))
    await callback.message.edit_text(
        "Вы уверены, что хотите отменить эту запись?",
        reply_markup=confirm_cancel_kb(aid),
    )
    await callback.answer()


@router.callback_query(F.data == "keep")
async def keep_appointment(callback: CallbackQuery):
    await callback.message.edit_text("Запись сохранена.")
    await callback.message.answer("Главное меню:", reply_markup=main_kb())
    await callback.answer()


@router.callback_query(F.data.startswith("cnf_"))
async def confirm_cancel(callback: CallbackQuery):
    from database import cancel_appointment
    aid = int(callback.data.replace("cnf_", ""))
    cancel_appointment(aid, callback.from_user.id)
    await callback.message.edit_text(" Запись отменена.")
    await callback.message.answer("Главное меню:", reply_markup=main_kb())
    await callback.answer()

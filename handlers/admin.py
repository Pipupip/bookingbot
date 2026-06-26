import logging

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import ADMIN_PASSWORD, SERVICES
from database import get_stats, get_today_appointments
from states.booking import AdminStates
from keyboards.menu import main_kb, admin_kb

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.text == "Админ-панель")
async def enter_admin(message: Message, state: FSMContext):
    await state.set_state(AdminStates.PASSWORD)
    await message.answer(" Введите пароль администратора:")


@router.message(AdminStates.PASSWORD)
async def check_password(message: Message, state: FSMContext):
    if message.text != ADMIN_PASSWORD:
        await message.answer(" Неверный пароль.")
        await state.clear()
        return
    await state.set_state(AdminStates.MENU)
    await message.answer(
        " Добро пожаловать в админ-панель!\n\n"
        "Выберите действие:",
        reply_markup=admin_kb(),
    )


@router.message(AdminStates.MENU, F.text == "Статистика")
async def show_stats(message: Message):
    stats = get_stats()
    await message.answer(
        f"   <b>Статистика</b>\n\n"
        f" Пользователей: {stats['users']}\n"
        f" Записей сегодня: {stats['today']}\n"
        f" Активных записей: {stats['active']}"
    )


@router.message(AdminStates.MENU, F.text == "Заявки на сегодня")
async def show_today(message: Message):
    apps = get_today_appointments()
    if not apps:
        await message.answer("На сегодня записей нет.")
        return
    text = "<b>Записи на сегодня:</b>\n\n"
    for a in apps:
        text += f" {a['time']} — {a['name']} ({a['service'][:15]})\n"
    await message.answer(text)


@router.message(AdminStates.MENU, F.text == "Добавить услугу")
async def add_service_start(message: Message, state: FSMContext):
    await state.set_state(AdminStates.ADD_SERVICE_NAME)
    await message.answer("Введите <b>название</b> новой услуги:")


@router.message(AdminStates.ADD_SERVICE_NAME)
async def add_service_name(message: Message, state: FSMContext):
    await state.update_data(new_name=message.text.strip())
    await state.set_state(AdminStates.ADD_SERVICE_PRICE)
    await message.answer("Введите <b>цену</b> новой услуги (в рублях):")


@router.message(AdminStates.ADD_SERVICE_PRICE)
async def add_service_price(message: Message, state: FSMContext):
    data = await state.get_data()
    name = data["new_name"]
    price = message.text.strip()
    SERVICES[name] = f"{name} — {price} руб."
    await message.answer(f" Услуга <b>{name}</b> добавлена!", reply_markup=admin_kb())
    await state.set_state(AdminStates.MENU)


@router.message(AdminStates.MENU, F.text == "Удалить услугу")
async def remove_service_start(message: Message, state: FSMContext):
    await state.set_state(AdminStates.REMOVE_SERVICE)
    lines = ["Выберите услугу для удаления (напишите название):\n"]
    for key in SERVICES:
        lines.append(f"• {key}")
    await message.answer("\n".join(lines))


@router.message(AdminStates.REMOVE_SERVICE)
async def remove_service_exec(message: Message, state: FSMContext):
    name = message.text.strip()
    if name in SERVICES:
        del SERVICES[name]
        await message.answer(f" Услуга <b>{name}</b> удалена!", reply_markup=admin_kb())
    else:
        await message.answer("Услуга не найдена. Попробуйте ещё раз:")
        return
    await state.set_state(AdminStates.MENU)


@router.message(AdminStates.MENU, F.text == "Выйти из админки")
async def exit_admin(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Вы вышли из админ-панели.", reply_markup=main_kb())


@router.message(AdminStates.MENU)
async def admin_unknown(message: Message):
    await message.answer("Используйте кнопки админ-панели.")

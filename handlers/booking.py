import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import ADMIN_CHAT_ID
from database import add_appointment, add_user
from states.booking import BookingStates
from keyboards.menu import main_kb, phone_kb
from keyboards.inline import services_kb, date_kb, time_kb, confirm_kb, review_kb

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.text == "Назад")
async def go_back(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено.", reply_markup=main_kb())


@router.message(F.text == "Записаться онлайн")
async def start_booking(message: Message, state: FSMContext):
    await state.set_state(BookingStates.WAITING_NAME)
    await message.answer(
        "   <b>Запись онлайн</b>\n\n"
        "Шаг 1 из 5: Введите <b>ваше имя</b>:",
        reply_markup=phone_kb(),
    )


@router.message(BookingStates.WAITING_NAME)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("Имя должно содержать минимум 2 символа.")
        return
    await state.update_data(client_name=name)
    await state.set_state(BookingStates.WAITING_PHONE)
    await message.answer(
        f" Приятно познакомиться, {name}!\n\n"
        "Шаг 2 из 5: Отправьте <b>номер телефона</b> кнопкой ниже или введите вручную:",
        reply_markup=phone_kb(),
    )


@router.message(BookingStates.WAITING_PHONE, F.contact)
async def process_phone_contact(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(client_phone=phone)
    await state.set_state(BookingStates.WAITING_SERVICE)
    await message.answer(
        f" Номер получен: <code>{phone}</code>\n\n"
        "Шаг 3 из 5: Выберите <b>услугу</b>:",
        reply_markup=services_kb(),
    )


@router.message(BookingStates.WAITING_PHONE)
async def process_phone_text(message: Message, state: FSMContext):
    phone = message.text.strip()
    digits = "".join(filter(str.isdigit, phone))
    if len(digits) < 10:
        await message.answer("Введите корректный номер (например, +7 999 123-45-67).")
        return
    await state.update_data(client_phone=phone)
    await state.set_state(BookingStates.WAITING_SERVICE)
    await message.answer(
        f" Номер принят: <code>{phone}</code>\n\n"
        "Шаг 3 из 5: Выберите <b>услугу</b>:",
        reply_markup=services_kb(),
    )


@router.callback_query(BookingStates.WAITING_SERVICE, F.data.startswith("svc_"))
async def process_service(callback: CallbackQuery, state: FSMContext):
    key = callback.data.replace("svc_", "", 1)
    from config import SERVICES
    desc = SERVICES.get(key, key)
    await state.update_data(selected_service=desc)
    await state.set_state(BookingStates.WAITING_DATE)
    await callback.message.edit_text(
        f" Вы выбрали: <b>{desc}</b>\n\n"
        "Шаг 4 из 5: Выберите <b>дату</b>:",
        reply_markup=date_kb(),
    )
    await callback.answer()


@router.callback_query(BookingStates.WAITING_DATE, F.data.startswith("date_"))
async def process_date(callback: CallbackQuery, state: FSMContext):
    date = callback.data.replace("date_", "", 1)
    await state.update_data(selected_date=date)
    await state.set_state(BookingStates.WAITING_TIME)
    await callback.message.edit_text(
        f" Дата: <b>{date}</b>\n\n"
        "Шаг 5 из 5: Выберите <b>время</b> (занятые скрыты):",
        reply_markup=time_kb(date),
    )
    await callback.answer()


@router.callback_query(F.data == "disabled")
async def slot_taken(callback: CallbackQuery):
    await callback.answer("Это время уже занято", show_alert=True)


@router.callback_query(BookingStates.WAITING_TIME, F.data.startswith("time_"))
async def process_time(callback: CallbackQuery, state: FSMContext):
    selected_time = callback.data.replace("time_", "", 1)
    await state.update_data(selected_time=selected_time)

    data = await state.get_data()
    name = data["client_name"]
    phone = data["client_phone"]
    service = data["selected_service"]
    date = data["selected_date"]

    await state.set_state(BookingStates.CONFIRM)
    await callback.message.edit_text(
        f"   <b>Проверьте данные:</b>\n\n"
        f" Имя: {name}\n"
        f" Тел: {phone}\n"
        f" Услуга: {service}\n"
        f" Дата: {date}\n"
        f" Время: {selected_time}\n\n"
        "Всё верно?",
        reply_markup=confirm_kb(),
    )
    await callback.answer()


@router.callback_query(BookingStates.CONFIRM, F.data == "confirm_yes")
async def confirm_booking(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    name = data["client_name"]
    phone = data["client_phone"]
    service = data["selected_service"]
    date = data["selected_date"]
    selected_time = data["selected_time"]

    aid = add_appointment(
        user_id=callback.from_user.id,
        name=name,
        phone=phone,
        service=service,
        date=date,
        time=selected_time,
    )

    if aid is None:
        await callback.message.edit_text(
            " К сожалению, это время уже кто-то занял.\n"
            f"Попробуйте другое время на {date}.",
        )
        await callback.message.answer(
            "Выберите другое время:", reply_markup=time_kb(date)
        )
        await state.set_state(BookingStates.WAITING_TIME)
        await callback.answer()
        return

    msg = (
        f"   <b>НОВАЯ ЗАЯВКА! </b>\n"
        f" {15*'━'}\n"
        f" Имя: {name}\n"
        f" Тел: {phone}\n"
        f" Услуга: {service}\n"
        f" Дата: {date}\n"
        f" Время: {selected_time}\n"
        f" ID: {callback.from_user.id}\n"
        f" {15*'━'}"
    )

    if ADMIN_CHAT_ID:
        try:
            await callback.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg)
        except Exception as e:
            logger.error(f"Ошибка отправки админу: {e}")

    await callback.message.edit_text(
        f"   <b>Запись подтверждена!</b>\n\n"
        f" Имя: {name}\n"
        f" Телефон: {phone}\n"
        f" Услуга: {service}\n"
        f" Дата: {date}\n"
        f" Время: {selected_time}\n\n"
        "Скоро свяжемся для подтверждения.",
    )

    await callback.message.answer(
        "Оцените наш сервис от 1 до 5 :",
        reply_markup=review_kb(),
    )

    await state.clear()
    await callback.answer()


@router.callback_query(BookingStates.CONFIRM, F.data == "confirm_no")
async def cancel_confirm(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Запись отменена.")
    await callback.message.answer("Главное меню:", reply_markup=main_kb())
    await callback.answer()

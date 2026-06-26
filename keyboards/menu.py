from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Записаться онлайн")],
            [KeyboardButton(text="Мои записи")],
            [KeyboardButton(text="Услуги и цены"), KeyboardButton(text="О нас")],
            [KeyboardButton(text="Контакты"), KeyboardButton(text="Админ-панель")],
        ],
        resize_keyboard=True,
    )


def phone_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отправить номер", request_contact=True)],
            [KeyboardButton(text="Назад")],
        ],
        resize_keyboard=True,
    )


def admin_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Статистика")],
            [KeyboardButton(text="Заявки на сегодня")],
            [KeyboardButton(text="Добавить услугу")],
            [KeyboardButton(text="Удалить услугу")],
            [KeyboardButton(text="Выйти из админки")],
        ],
        resize_keyboard=True,
    )

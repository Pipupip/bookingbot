from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from database import add_review
from keyboards.inline import review_kb
from keyboards.menu import main_kb

router = Router()


@router.callback_query(F.data.startswith("rate_"))
async def process_rating(callback: CallbackQuery):
    rating = int(callback.data.replace("rate_", ""))
    add_review(callback.from_user.id, rating)
    stars = "⭐" * rating
    await callback.message.edit_text(
        f" Спасибо за оценку {stars}!\n"
        "Будем рады видеть вас снова!",
    )
    await callback.message.answer("Главное меню:", reply_markup=main_kb())
    await callback.answer()

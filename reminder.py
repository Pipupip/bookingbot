import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import Bot

from database import get_upcoming_appointments, mark_notified

logger = logging.getLogger(__name__)


async def reminder_loop(bot: Bot):
    while True:
        try:
            now = datetime.now()
            target = (now + timedelta(hours=24)).strftime("%Y-%m-%d")
            time_target = now.strftime("%H:%M")

            appointments = get_upcoming_appointments()
            for a in appointments:
                try:
                    await bot.send_message(
                        chat_id=a["user_id"],
                        text=(
                            f"   <b>Напоминание!</b>\n\n"
                            f"У вас запись на <b>завтра</b>:\n"
                            f" {a['service']} в {a['time']}\n\n"
                            f"Ждём вас!"
                        ),
                    )
                    mark_notified(a["id"])
                    logger.info(f"Напоминание отправлено пользователю {a['user_id']}")
                except Exception as e:
                    logger.error(f"Ошибка напоминания {a['user_id']}: {e}")

        except Exception as e:
            logger.error(f"Ошибка в цикле напоминаний: {e}")

        await asyncio.sleep(3600)

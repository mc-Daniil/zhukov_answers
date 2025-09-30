import logging
import random
import re
from pathlib import Path
import html

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram import Router
from aiogram.types import ReplyParameters

from config import BOT_TOKEN, STICKER_PACK_ID

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()
dp.include_router(router)

sticker_file_ids = []
async def fetch_stickers():
    global sticker_file_ids
    try:
        sticker_set = await bot.get_sticker_set(STICKER_PACK_ID)
        sticker_file_ids = [sticker.file_id for sticker in sticker_set.stickers]
        logging.info("Fetched %d stickers from %s", len(sticker_file_ids), STICKER_PACK_ID)
    except Exception as e:
        logging.exception("Error fetching sticker set '%s'", STICKER_PACK_ID)


ANSWERS_VOT = [
    "Молодой человек!",
    "Непонятно объясняю?",
    "Ааааааааааах",
    "Вооооооооот",
    "Молодой человек, вы куда",
]

ANSWERS_QUESTION = ["Это было на лекции!", "Это было на лекции..."]


@router.message()
async def check_message(message: types.Message):
    text = message.text or ""

    match_vot = re.search(r'в+о+т', text, re.IGNORECASE)
    if match_vot:
        found = match_vot.group(0)
        position = match_vot.start()
        found_safe = html.escape(found)
        if random.choice([True, False]):
            if sticker_file_ids:
                sticker = random.choice(sticker_file_ids)
                try:
                    await bot.send_sticker(
                        chat_id=message.chat.id,
                        sticker=sticker,
                        reply_parameters=ReplyParameters(
                            message_id=message.message_id,
                            quote=found_safe,
                            quote_position=len(text[:position]),
                        ),
                    )
                except Exception:
                    logging.exception("Failed to send sticker")
                    await bot.send_message(
                        chat_id=message.chat.id,
                        text="Ошибка при отправке стикера.",
                        reply_parameters=ReplyParameters(
                            message_id=message.message_id,
                            quote=found_safe,
                            quote_position=len(text[:position]),
                        ),
                    )
            else:
                await bot.send_message(
                    chat_id=message.chat.id,
                    text="Sticker pack not found or empty.",
                    reply_parameters=ReplyParameters(
                        message_id=message.message_id,
                        quote=found_safe,
                        quote_position=len(text[:position]),
                    ),
                )
        else:
            # Отправить сообщение из ANSWERS_VOT
            answer = random.choice(ANSWERS_VOT)
            await bot.send_message(
                chat_id=message.chat.id,
                text=answer,
                reply_parameters=ReplyParameters(
                    message_id=message.message_id,
                    quote=found_safe,
                    quote_position=len(text[:position]),
                ),
            )

    if '?' in text and random.choice([True, False]):
        answer = random.choice(ANSWERS_QUESTION)
        await bot.send_message(
            chat_id=message.chat.id,
            text=answer,
            reply_parameters=ReplyParameters(
                message_id=message.message_id,
            ),
        )

    return


async def main():
    await fetch_stickers()
    await dp.start_polling(bot)


if __name__ == '__main__':
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('Shutdown requested')
    except Exception:
        import traceback
        traceback.print_exc()
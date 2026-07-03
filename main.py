import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from config.data import BOT_TOKEN
from database import Database
from ai_agent import AIAgent

dp = Dispatcher()
db = Database()
agent = AIAgent(db=db)

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    telegram_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username

    await db.create_user(telegram_id, full_name, username)

    await message.answer("Salom!. Sizga qanday yordam bera olaman?")

@dp.message()
async def ai_message_handler(message: Message) -> None:
    if not message.text:
        return

    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    reply = await agent.get_response(telegram_id=message.from_user.id, user_message=message.text)
    
    await message.answer(reply)

async def main() -> None:
    await db.create_tables()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("See you later my baby!! 🥹 ")
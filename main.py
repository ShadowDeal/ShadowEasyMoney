
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
import aiohttp
import os

API_TOKEN = os.getenv("API_TOKEN")
LAVA_API_KEY = os.getenv("LAVA_API_KEY")
SHOP_ID = os.getenv("SHOP_ID")
FILE_PATH = "sxema_keshbek_shadowdeal_v2.pdf"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Купить за 500₽", callback_data="buy")
    )
    await message.answer(
        "Привет! Здесь ты можешь купить серую схему по кешбэку и возврату товара.\n\nЦена: 500₽",
        reply_markup=kb
    )

@dp.callback_query_handler(lambda c: c.data == "buy")
async def buy_scheme(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    payload = {
        "shop_id": SHOP_ID,
        "amount": 500,
        "currency": "RUB",
        "comment": f"user_{user_id}",
        "success_url": "https://t.me/shadowdealbot",
        "fail_url": "https://t.me/shadowdealbot"
    }

    headers = {
        "Authorization": f"Bearer {LAVA_API_KEY}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.lava.ru/business/invoice", headers=headers, json=payload) as resp:
            data = await resp.json()
            url = data.get("data", {}).get("url")
            if url:
                await bot.send_message(user_id, f"Оплати по ссылке:\n{url}\n\nПосле оплаты схема придёт автоматически.")
            else:
                await bot.send_message(user_id, "Ошибка при генерации ссылки. Попробуй позже.")

@dp.message_handler(commands=["send_file"])
async def send_file(message: types.Message):
    with open(FILE_PATH, "rb") as f:
        await message.answer_document(types.InputFile(f, filename="sxema_shadowdeal.pdf"))

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

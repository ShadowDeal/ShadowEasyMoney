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
        "success_url": "https://t.me/Easy_shadow_moneybot",
        "fail_url": "https://t.me/Easy_shadow_moneybot"
    }

    headers = {
        "Authorization": f"Bearer {LAVA_API_KEY}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.lava.ru/invoice", json=payload, headers=headers) as response:
            result = await response.json()

            if response.status != 200 or "data" not in result:
                await callback_query.message.answer(f"Ошибка при генерации: {result}")
                return

            invoice_url = result["data"]["invoice_url"]
            await callback_query.message.answer(f"Ссылка на оплату: {invoice_url}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

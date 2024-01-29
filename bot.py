import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from btns import *
from states import *
from utils import *
from database import *
import os


BOT_TOKEN = "6008616711:AAGCSYfTv25oXl48EMIqs75T9ELBWbfwlW0"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, parse_mode='html')
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)


async def command_menu(dp: Dispatcher):
    await dp.bot.set_my_commands(
        [
            types.BotCommand('start', 'Ishga tushirish'),
            types.BotCommand('help', 'yordam'),
        ]
    )


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    btn = await start_btn()
    await message.answer('Xush kelibsiz birodar!', reply_markup=btn)


@dp.message_handler(text="💫 Rasim Effect berish")
async def effect_to_image_handler(message: types.Message):
    btn = await filters_btn(filters)
    await message.answer("Filterlardan birini tanlang:", reply_markup=btn)


@dp.message_handler(state=UserStates.get_image, content_types=['photo', 'text'])
async def get_image_handler(message: types.Message, state: FSMContext):
    content = message.content_type

    if content == "text":
        await effect_to_image_handler(message)
    else:
        filename = f"rasim_{message.from_user.id}.jpg"
        await message.photo[-1].download(destination_file=filename)
        await message.answer("Rasim qabul qilindi!")

        data = await state.get_data()
        await filter_user_image(filename, data['filter'])
        await message.answer_photo(
            photo=types.InputFile(filename),
            caption=f"Rasim Tayyor :)"
        )
        os.remove(filename)
        await start_command(message)
    await state.finish()



@dp.message_handler(content_types=['text'])
async def selected_filter_handler(message: types.Message, state: FSMContext):
    text = message.text

    if text in filters:
        await state.update_data(filter=text)
        btn = await cancel_btn()
        await message.answer("Rasimni yuboring:", reply_markup=btn)
        await UserStates.get_image.set()

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=command_menu)
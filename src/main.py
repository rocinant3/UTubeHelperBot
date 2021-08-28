import os

from aiogram import Bot, types, Dispatcher, executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from services.youtube import YoutubeService
from utils.youtube import is_valid_url
from exceptions import youtube as youtube_exceptions


BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GOOGLE_DEVELOPER_KEY = os.getenv("GOOGLE_DEVELOPER_KEY", "")
BITLY_API_KEY = os.getenv("BITLY_API_KEY", "")

bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot=bot, storage=MemoryStorage())


class ServiceProcess(StatesGroup):
    choice_mode = State()
    enter_link = State()
    enter_description = State()
    end = State()


async def set_commands(_bot: Bot):
    commands = [
        types.BotCommand(command="/start", description="Начать"),
    ]
    await _bot.set_my_commands(commands)


@dp.message_handler(commands="start")
async def start(message: types.Message,  state: FSMContext):
    await state.reset_state()
    await ServiceProcess.choice_mode.set()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    m_button = types.InlineKeyboardButton(text="Ручной")
    a_button = types.InlineKeyboardButton(text="Авто")
    buttons = [m_button, a_button]
    keyboard.add(*buttons)

    await message.answer('Режим', reply_markup=keyboard)


@dp.message_handler(state=ServiceProcess.choice_mode)
async def choice_mode(message: types.Message, state: FSMContext):
    if message.text == "Ручной":
        await ServiceProcess.enter_link.set()
        await message.answer('Введите ссылку')
        await state.update_data(mode='manual')
    elif message.text == "Авто":
        await ServiceProcess.enter_link.set()
        await message.answer("Введите ссылку")
        await state.update_data(mode="auto")
    else:
        await message.answer('Неверная команда')


_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
_start_button = types.InlineKeyboardButton(text="Да")
_buttons = [_start_button]
_keyboard.add(*_buttons)


@dp.message_handler(state=ServiceProcess.enter_link)
async def enter_link(message: types.Message, state: FSMContext):
    if not is_valid_url(message.text):
        await message.reply("Невалидная ссылка")
    else:
        await state.update_data(link=message.text)
        state_data = await state.get_data()
        mode = state_data['mode']
        if mode == 'auto':
            await ServiceProcess.end.set()
            await message.reply(text="Подвердить", reply_markup=_keyboard)
        elif mode == "manual":
            await ServiceProcess.enter_description.set()
            await message.answer("Введите описание видео")


@dp.message_handler(state=ServiceProcess.enter_description)
async def enter_description(message: types.Message, state: FSMContext):
    if message.text == "":
        await message.answer("Пустое сообщение")
    else:
        await state.update_data(description=message.text)
        await ServiceProcess.end.set()
        await message.reply(text="Подвердить", reply_markup=_keyboard)


@dp.message_handler(state=ServiceProcess.end)
async def end(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    link = state_data['link']
    mode = state_data['mode']

    try:

        youtube_service = YoutubeService(dev_key=GOOGLE_DEVELOPER_KEY, bitly_key=BITLY_API_KEY)
        if mode == 'manual':
            description = state_data['description']
            video_id = youtube_service.parse_video_id(link)
            shorted_links = youtube_service.short_links(description, video_id)
        else:
            shorted_links = youtube_service.get_short_links_for_video_time_codes(link)
        await message.reply(youtube_service.shorted_links_to_html(shorted_links))
    except youtube_exceptions.InvalidURLError:
        await message.reply("Невалидная Youtube ссылка")
    except youtube_exceptions.VideoDoesntExistError:
        await message.reply("Видео не найдено")
    except youtube_exceptions.TimeCodesDoesntExistError:
        await message.reply("Тайм коды не найдены")
    await state.reset_state()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

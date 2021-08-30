from decouple import config
from aiogram import Bot, types, Dispatcher, executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from services.youtube import YoutubeService
from utils.youtube import is_valid_url
from utils.bot import build_keyboard
from utils.core import batch
from exceptions import youtube as youtube_exceptions


BOT_TOKEN = config("BOT_TOKEN")
GOOGLE_DEVELOPER_KEY = config("GOOGLE_DEVELOPER_KEY")
BITLY_API_KEY = config("BITLY_API_KEY")

bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot=bot, storage=MemoryStorage())


yes_or_no_kb = build_keyboard(("Да", "Нет"), one_time=True)  # type: ignore
agree_kb = build_keyboard(("Подтвердить", ), one_time=True)  # type: ignore


class ServiceState(StatesGroup):
    choice_mode = State()
    enter_link = State()
    enter_description = State()
    short_links = State()
    replace_http = State()
    end = State()


async def set_commands(_bot: Bot):
    commands = [
        types.BotCommand(command="/start", description="Начать"),
    ]
    await _bot.set_my_commands(commands)


@dp.message_handler(commands="start")
async def start(message: types.Message,  state: FSMContext):
    await state.reset_state()
    await ServiceState.choice_mode.set()
    keyboard = build_keyboard(("Ручной", "Авто"), one_time=True)
    await message.answer('Режим', reply_markup=keyboard)


@dp.message_handler(state=ServiceState.choice_mode)
async def choice_mode(message: types.Message, state: FSMContext):
    if message.text == "Ручной":
        await ServiceState.enter_link.set()
        await message.answer('Введите ссылку')
        await state.update_data(mode='manual')
    elif message.text == "Авто":
        await ServiceState.enter_link.set()
        await message.answer("Введите ссылку")
        await state.update_data(mode="auto")
    else:
        await message.answer('Неверная команда')


@dp.message_handler(state=ServiceState.enter_link)
async def enter_link(message: types.Message, state: FSMContext):
    if not is_valid_url(message.text):
        await message.reply("Невалидная ссылка")
    else:
        await state.update_data(link=message.text)
        state_data = await state.get_data()
        mode = state_data['mode']
        if mode == 'auto':
            await ServiceState.short_links.set()
            await message.reply(text="Сокращать ссылки?", reply_markup=yes_or_no_kb)
        elif mode == "manual":
            await ServiceState.enter_description.set()
            await message.answer("Введите описание видео")


@dp.message_handler(state=ServiceState.enter_description)
async def enter_description(message: types.Message, state: FSMContext):
    if message.text == "":
        await message.answer("Пустое сообщение")
    else:
        await state.update_data(description=message.text)
        await ServiceState.short_links.set()
        await message.reply(text="Сокращать ссылки?", reply_markup=yes_or_no_kb)


@dp.message_handler(state=ServiceState.short_links)
async def short_links(message: types.Message, state: FSMContext):
    if message.text not in ["Да", "Нет"]:
        await message.answer("Введите Да или Нет")
    else:
        if message.text == "Да":
            await state.update_data(short_links=True)
        elif message.text == "Нет":
            await state.update_data(short_links=False)

        await ServiceState.replace_http.set()
        await message.reply("Заменять https?", reply_markup=yes_or_no_kb)


@dp.message_handler(state=ServiceState.replace_http)
async def replace_http(message: types.Message, state: FSMContext):
    if message.text not in ["Да", "Нет"]:
        await message.answer("Введите Да или Нет")
    else:
        if message.text == "Да":
            await state.update_data(replace_http=True)
        elif message.text == "Нет":
            await state.update_data(replace_http=False)
        await ServiceState.end.set()
        await message.reply("Подтвердить", reply_markup=agree_kb)


@dp.message_handler(state=ServiceState.end)
async def end(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    link = state_data['link']
    mode = state_data['mode']
    http_replace = state_data['replace_http']
    short_the_links = state_data['short_links']

    try:

        youtube_service = YoutubeService(dev_key=GOOGLE_DEVELOPER_KEY, bitly_key=BITLY_API_KEY)
        if mode == 'manual':
            description = state_data['description']
            video_id = youtube_service.parse_video_id(link)
            shorted_links = youtube_service._extract_time_codes(description, video_id, short_the_links)
        else:
            shorted_links = youtube_service.extract_time_codes(link, short_the_links)
            html_message = youtube_service.time_codes_to_html(shorted_links, http_replace)
            if len(html_message) > 4096:
                for batched_message in batch(html_message.split("\n"),  25):
                    final_message = ""
                    for mess in batched_message:
                        final_message += f'{mess}\n'
                    await message.reply(final_message)

            else:
                await message.reply(html_message)
    except youtube_exceptions.InvalidURLError:
        await message.reply("Невалидная Youtube ссылка")
    except youtube_exceptions.VideoDoesntExistError:
        await message.reply("Видео не найдено")
    except youtube_exceptions.TimeCodesDoesntExistError:
        await message.reply("Тайм коды не найдены")
    await state.reset_state()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

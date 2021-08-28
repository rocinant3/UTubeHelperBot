import os

from aiogram import Bot, types, Dispatcher, executor

from services.youtube import YoutubeService
from utils.youtube import is_valid_url
from exceptions import youtube as youtube_exceptions

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GOOGLE_DEVELOPER_KEY = os.getenv("GOOGLE_DEVELOPER_KEY", "")
BITLY_API_KEY = os.getenv("BITLY_API_KEY", "")


bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot=bot)


@dp.message_handler()
async def message_handler(message: types.Message):
    if not is_valid_url(message.text):
        await message.reply("Невалидная ссылка")
    else:
        try:
            youtube_service = YoutubeService(dev_key=GOOGLE_DEVELOPER_KEY, bitly_key=BITLY_API_KEY)
            shorted_links = youtube_service.get_short_links_on_video_time_codes(message.text)
            await message.reply(youtube_service.shorted_links_to_html(shorted_links))
        except youtube_exceptions.InvalidURLError:
            await message.reply("Невалидная Youtube ссылка")
        except youtube_exceptions.VideoDoesntExistError:
            await message.reply("Видео не найдено")
        except youtube_exceptions.TimeCodesDoesntExistError:
            await message.reply("Тайм коды не найдены")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

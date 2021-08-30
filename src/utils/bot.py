from aiogram import types


def build_keyboard(buttons: tuple, one_time: bool = True):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=one_time)
    _buttons = [types.InlineKeyboardButton(text=txt) for txt in buttons]
    kb.add(*_buttons)
    return kb

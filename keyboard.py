from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


inline_btn_place = InlineKeyboardButton('Разместить', callback_data='place')
place = InlineKeyboardMarkup().row(inline_btn_place)


inline_btn_link = InlineKeyboardButton('Добавить объявление', url='t.me/ekbvape_bot')
link = InlineKeyboardMarkup().row(inline_btn_link)
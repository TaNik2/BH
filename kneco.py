from main import bot, dp
import asyncio
from aiogram import types
import keyboard as kb
from data_base import User
import text as txt
import datetime as dt
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from typing import Union, List
from config import ADMIN_ID, CHANNEL_ID


class AlbumMiddleware(BaseMiddleware):
    album_data: dict = {}

    def __init__(self, latency: Union[int, float] = 0.01):
        self.latency = latency
        super().__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        if not message.media_group_id:
            return

        try:
            self.album_data[message.media_group_id].append(message)
            raise CancelHandler()  # Tell aiogram to cancel handler for this group element
        except KeyError:
            self.album_data[message.media_group_id] = [message]
            await asyncio.sleep(self.latency)

            message.conf["is_last"] = True
            data["album"] = self.album_data[message.media_group_id]

    async def on_post_process_message(self, message: types.Message, result: dict, data: dict):
        if message.media_group_id and message.conf.get("is_last"):
            del self.album_data[message.media_group_id]


'''
-----------------------------------------------------------
commands
-----------------------------------------------------------
'''


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    tg_id = message.from_user.id
    u, is_created = User.get_or_create(
        tg_id=tg_id
    )
    try:
        msg = message.text
        ref_id = msg.split(' ')[1]
        if len(msg) > 6 and ref_id != tg_id:
            ref_parent = User.get(tg_id=ref_id)
            ref_parent.ref += 1
            ref_parent.save()
        await bot.send_message(message.from_user.id, txt.start)
    except:
        await bot.send_message(message.from_user.id, txt.start)


@dp.message_handler(commands=['send'])
async def database_for_stupid_admin(message: types.Message):
    if message.reply_to_message:
        for user in User.select():
            try:
                await bot.send_message(user.tg_id, message.reply_to_message.text)
            except:
                pass


@dp.message_handler(commands=['sendbd'])
async def process_command_join(message: types.Message):
    db = types.InputFile('users.db')
    await bot.send_document(message.from_user.id, db)


@dp.message_handler(commands=['referal'])
async def database_for_stupid_admin(message: types.Message):
    await bot.send_message(message.from_user.id,
                           f'Ваша реферальная ссылка - https://t.me/ekbvape_bot?start={message.from_user.id}\nВажно, чтобы человек подписался на канал, ну и желательно чтобы ему действительно интересна была эта тематика, всё будем просматривать)\nЭто для розыгрышей к слову)',
                           disable_web_page_preview=True)


@dp.message_handler(content_types=['photo', 'text', 'video'])
async def post(message: types.Message, album: List[types.Message] = None):
    user, is_created = User.get_or_create(tg_id=message.from_user)
    user_channel_status = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=message.from_user.id)
    if user_channel_status["status"] != 'left':
        if user.time <= dt.datetime.now():
            if message.media_group_id:
                media_group = types.MediaGroup()
                i = 0
                for obj in album:
                    if obj.photo:
                        file_id = obj.photo[-1].file_id
                    else:
                        file_id = obj[obj.content_type].file_id
                    try:
                        if i == 0:
                            media_group.attach({"media": file_id, "type": obj.content_type,
                                                "caption": obj.caption + f'\n<b>Автор</b>: <a href="tg://user?id={message.chat.id}">{message.chat.first_name}</a>' if obj.caption else f'\n<b>Автор</b>: <a href="tg://user?id={message.chat.id}">{message.chat.first_name}</a>'})
                        else:
                            media_group.attach({"media": file_id, "type": obj.content_type})
                        i += 1
                    except:
                        media_group.attach({"media": file_id, "type": obj.content_type,
                                            "caption": obj.caption})
                    post.media_group = media_group
            await bot.send_message(message.from_user.id, 'Ваше объявление:',
                                   reply_to_message_id=message.message_id,
                                   reply_markup=kb.place)
        else:
            time = user.time - dt.datetime.now()
            time = str(time).split('.')[0].split(':')
            await bot.send_message(message.from_user.id,
                                   f'Следующее объявление можно будет выложить через <b>{time[0]}ч.{time[1]}мин.{time[2]}сек.</b>')

    else:
        await bot.send_message(message.from_user.id, 'Пожалуйста, подпишитесь на канал @ekbvape')


@dp.callback_query_handler(lambda c: c.data == 'place')
async def process_place(callback_query: types.CallbackQuery):
    user = User.get(tg_id=callback_query.from_user.id)
    if user.time <= dt.datetime.now():
        user.time = dt.datetime.now()
        user.time += dt.timedelta(days=0, hours=2, minutes=0, seconds=0)
        user.save()
        try:
            await bot.send_message(CHANNEL_ID,
                                   callback_query.message.reply_to_message.text + f'\n<b>Автор</b>: <a href="tg://user?id={callback_query.message.chat.id}">{callback_query.message.chat.first_name}</a>')
            await bot.send_message(CHANNEL_ID, '<b>Наш чат</b> - @ekbvape_chat\n<b>Реклама</b> - @ekbvape_admin\n<b>Лучший VapeShop</b> - @vapeshopnation',
                                   reply_markup=kb.link)
        except:
            if callback_query.message.reply_to_message.media_group_id:
                await bot.send_media_group(CHANNEL_ID, post.media_group)
                await bot.send_message(CHANNEL_ID, '<b>Наш чат</b> - @ekbvape_chat\n<b>Реклама</b> - @ekbvape_admin\n<b>Лучший VapeShop</b> - @vapeshopnation',
                                       reply_markup=kb.link)
            else:
                if callback_query.message.reply_to_message.caption is not None:
                    if callback_query.message.reply_to_message.photo:
                        await bot.send_photo(CHANNEL_ID, callback_query.message.reply_to_message.photo[2].file_id,
                                             caption=str(
                                                 callback_query.message.reply_to_message.caption) + f'\n<b>Автор</b>: <a href="tg://user?id={callback_query.message.chat.id}">{callback_query.message.chat.first_name}</a>')
                    else:
                        await bot.send_video(CHANNEL_ID, callback_query.message.reply_to_message.video.file_id,
                                             caption=str(
                                                 callback_query.message.reply_to_message.caption) + f'\n<b>Автор</b>: <a href="tg://user?id={callback_query.message.chat.id}">{callback_query.message.chat.first_name}</a>')
                    await bot.send_message(CHANNEL_ID,
                                           '<b>Наш чат</b> - @ekbvape_chat\n<b>Реклама</b> - @ekbvape_admin\n<b>Лучший VapeShop</b> - @vapeshopnation',
                                           reply_markup=kb.link)
                else:
                    if callback_query.message.reply_to_message.photo:
                        await bot.send_photo(CHANNEL_ID, callback_query.message.reply_to_message.photo[2].file_id,
                                             f'\n<b>Автор</b>: <a href="tg://user?id={callback_query.message.chat.id}">{callback_query.message.chat.first_name}</a>')
                    else:
                        await bot.send_video(CHANNEL_ID, callback_query.message.reply_to_message.video.file_id,
                                             caption=f'\n<b>Автор</b>: <a href="tg://user?id={callback_query.message.chat.id}">{callback_query.message.chat.first_name}</a>')
                    await bot.send_message(CHANNEL_ID,
                                           '<b>Наш чат</b> - @ekbvape_chat\n<b>Реклама</b> - @ekbvape_admin\n<b>Лучший VapeShop</b> - @vapeshopnation',
                                           reply_markup=kb.link)
        await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
        await bot.send_message(callback_query.from_user.id, txt.end)
    else:
        time = user.time - dt.datetime.now()
        time = str(time).split('.')[0].split(':')
        await bot.send_message(callback_query.from_user.id,
                               f'Следующее объявление можно будет выложить через <b>{time[0]}ч.{time[1]}мин.{time[2]}сек.</b>')

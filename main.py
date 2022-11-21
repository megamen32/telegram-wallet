import asyncio
import datetime
import json
import os.path
import traceback

import aioschedule
import requests
from aiogram import Dispatcher, Bot,types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
API_TOKEN = '5745167755:AAEN6jIKnLayatN1Iyjtf1aDsy2LFD2AbPU'
bot = Bot(token=API_TOKEN, timeout=140)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


USERS=[]
if os.path.exists('users.txt'):
    USERS=json.load(open('users.txt','r'))


def find(iter,func):
    for elem in iter:
        if func(elem):return elem
    return None
async def sleep_and_run(time,func):
    await asyncio.sleep(time)
    await func
async def load():
    global USERS
    if os.path.exists('users.txt'):
        USERS = json.load(open('users.txt', 'r'))
    else:
        USERS=[]
async def save():
    global USERS
    json.dump(USERS,'users.txt')
async def on_startup(_):
    asyncio.create_task(load())

async def on_shutdown(_):
    asyncio.create_task(save())


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    print(f'user {message.from_user}')
    if message.chat.id not in user_ids:
        user_ids.append(message.chat.id)
        json.dump(user_ids,open('user_ids.txt','w'))
    await message.reply("Привет я бот для напоминаний")
@dp.message_handler(commands=['stats'])
async def sendstats(message: types.Message):
    new_clients=requests.get('http://demiurge.space:8888/clients/',timeout=15).json()
    texts=[]
    for client in new_clients:
        last_active = (client['last_active'])
        date = datetime.datetime.strptime(last_active, '%Y-%m-%d %H:%M:%S.%f')

        now = datetime.datetime.now() - date
        notification_text = f"Клиент {client['ip']} не отвечает уже {now.total_seconds() / 60:0.01f} минут!"
        texts+=[notification_text]
    await message.reply("\n".join(texts))
@dp.message_handler()
async def echo(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)
    print(message)
    notification.put(message.text)

async def send_all(message,exclude=[]):

    for id in user_ids:
        if id in exclude:continue
        try:
            await bot.send_message(id,message)
        except:traceback.print_exc()

if __name__ == '__main__':


    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
import telebot
import re
import requests
import json
import sqlite3
from telebot.types import Message
import os
from datetime import datetime, timedelta
from background import keep_alive
import time

# Список файлів з хендлерами та іншими функціями
import handler_karma_status
import handler_karma_handler
from sender_warloses import daily_scheduler_run, get_latest_statistics

bot = telebot.TeleBot(os.environ['bot_token'])

# Обробник команди karma_status. Відправляю дашборд по кармі в групу
@bot.message_handler(commands=['karma_status'])
def karma_status(message):
    gggg = message.chat.type
    print(gggg)
    handler_karma_status.karma_status(message)

# Обробник команди war_losses. Відправляє статистику по втратам в групу
@bot.message_handler(commands=['war_losses'])
def war_losses(message):
    get_latest_statistics()

# Обробник додавання та віднімання карми (карма+ / карма-) 

# Визначення глобальної змінної karma_regex (пошук слова Карма+- без врахування регістру)
karma_regex = re.compile(r'.*(карма\s*[+\-]).*', re.IGNORECASE)

@bot.message_handler(func=lambda message: message.chat.type == 'group' or message.chat.type == 'supergroup'  and karma_regex.search(message.text))
def karma_handler(message):
    handler_karma_handler.karma_handler(message)

# Запускаєм flask сервер (веб-сервіс, який пінгується монітором, щоб дозволяє звлишити replit активним)
keep_alive()

# Запускаєм відправку повідомлень за розкладом
daily_scheduler_run()

# Запускаємо бота
bot.infinity_polling()

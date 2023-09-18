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
import sched

# Визначення глобальної змінної karma_regex (пошук слова Карма+- без врахування регістру)
karma_regex = re.compile(r'.*(карма\s*[+\-]).*', re.IGNORECASE)
# Список файлів з хендлерами
import handler_karma_status
import handler_karma_handler

bot = telebot.TeleBot(os.environ['bot_token'])

# Обробник команди karma_status. Відправляю дашборд по кармі в групу
@bot.message_handler(commands=['karma_status'])
def karma_status(message):
    handler_karma_status.karma_status(message)
    
@bot.message_handler(func=lambda message: message.chat.type == 'group' and karma_regex.search(message.text))
def karma_handler(message):
    handler_karma_handler.karma_handler(message)
    
# Запускаєм flask сервер
keep_alive()

# Запускаємо бота
bot.infinity_polling()

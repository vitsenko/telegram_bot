import telebot
import re
import requests
import json
import sqlite3
from telebot.types import Message
import os
from datetime import datetime, timedelta
import schedule
import time
from threading import Thread

bot = telebot.TeleBot(os.environ['bot_token'])

group_chat_id = os.environ['group_chat_id']


def send_statistics_to_telegram(data):
    # Створення повідомлення з інформацією
    message = f"<code>{data['data']['date']}</code>\n"
    message += f"<code>{data['data']['day']}-й день війни</code>\n"
     
    message += "<b>\nTOTAL LOSSES\n</b>"
    stats = data['data']['stats']
    increase = data['data']['increase']
    
    for key, value in stats.items():
        # Перевірка, чи є відповідний ключ в словнику increase та чи більше за 0
        if key in increase and increase[key] > 0:
            message += f"{key}: {value}"+f"<b> (+{increase[key]})\n</b>"
            
        else:
            message += f"{key}: {value}\n"
                
    # Надсилання повідомлення у групу
    bot.send_message(group_chat_id, message, parse_mode='HTML')   

def get_latest_statistics():
    url = "https://russianwarship.rip/api/v2/statistics/latest"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            send_statistics_to_telegram(data)  # Відправляємо інформацію в телеграм групу
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")


# Функція, яка буде викликана щоденно о 9:00
def send_daily_statistics():
    current_time = datetime.now().time()
    if current_time.hour == 9 and current_time.minute == 0:
        get_latest_statistics()


# Розклад для виклику щоденної функції о 9:00

def daily_scheduler():
    schedule.every().day.at("9:00").do(send_daily_statistics)
    while True:
        schedule.run_pending()
        time.sleep(59)  # Зачекайте 1 хвилину перед перевіркою розкладу

def daily_scheduler_run():
    loses = Thread(target = daily_scheduler)
    loses.start()


import telebot
import re
import requests
import json
import sqlite3
from telebot.types import Message
import os
from datetime import datetime, timedelta


bot = telebot.TeleBot(os.environ['bot_token'])

def karma_status(message):
    # Підключення до БД
    conn = sqlite3.connect('telebot.db')
    cursor = conn.cursor()
    chat_id = message.chat.id
    print(chat_id)
    
    # Отримання списку всіх користувачів і їхньої карми
    cursor.execute("SELECT * FROM users")
    users_list = cursor.fetchall()

    allusers_karma = []
    if users_list:
        for user_info in users_list:
            user_karma = []
            
            cursor.execute("SELECT SUM(add_karma) FROM karma_data WHERE mentioned_user_id = ?", (user_info[0],))
            total_user_karma = cursor.fetchone()[0]

            user_karma.append(user_info[2])
            user_karma.append(total_user_karma)
            allusers_karma.append(user_karma)
        
    # Закрити підключення до БД
    cursor.close()
    conn.close()
    heart_emoji = "\U00002764"
    karma_text = f"<b>{heart_emoji} Статус карми:\n</b>"
    for user1, karma in allusers_karma:
        if karma != None:
            karma_text += f"{user1}: {karma}\n"
        else:
            karma_text += f"{user1}: - \n"
    # Відправка повідомлення зі списком карми
    bot.reply_to(message, karma_text, parse_mode = 'HTML')
    
    chat_id = message.chat.id
    message_id = message.message_id
    bot.delete_message(chat_id, message_id)
    
    user_id = message.from_user.id
    username = message.from_user.username
    
    print(f'karma_status - done\nrequest from {username}\id{user_id}')
    
   

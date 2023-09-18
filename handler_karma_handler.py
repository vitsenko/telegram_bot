import telebot
import re
import requests
import json
import sqlite3
from telebot.types import Message
import os
from datetime import datetime, timedelta


karma_regex = re.compile(r'.*(карма\s*[+\-]).*', re.IGNORECASE)

bot = telebot.TeleBot(os.environ['bot_token'])

def karma_handler(message):
    global add_karma_to
    add_karma_to = True

    # Підключення до БД
    conn = sqlite3.connect('telebot.db')
    cursor = conn.cursor()

    # Отримати інформацію про повідомлення
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    chat_id = message.chat.id
    text = message.text
        
    # Пошук збільшення або зменшення карми
    match = karma_regex.search(text)
    if match:
        karma_change = match.group(1)
        if karma_change.lower() == 'карма +':
            karma_value = 1
        elif karma_change.lower() == 'карма -':
            karma_value = -1
        else:
            karma_value = 0  # Якщо не вдалося визначити значення карми

        # Знайти згаданого користувача, відзначеного в повідомленні
        mentioned_username = None
        for entity in message.entities:
            if entity.type == 'text_mention':
                mentioned_user = entity.user
                
                if mentioned_user:
                    mentioned_user_id = mentioned_user.id
                    mentioned_user_username = mentioned_user.username
                    mentioned_user_first_name = mentioned_user.first_name
                    mentioned_user_last_name = mentioned_user.last_name

                    # Виконання SQL-запиту для отримання first_name та last_name за username
                    cursor.execute("SELECT first_name, last_name FROM users WHERE username=?", (mentioned_user_username,))
                    result = cursor.fetchone()
                    if result:
                        first_name, last_name = result
                        mentioned_user_first_name = first_name
                        mentioned_user_last_name = last_name
            else:
                # Регулярний вираз для пошуку імені користувача в тексті повідомлення
                username_regex = re.compile(r'@(\w+)')
            
                # Знаходження імені користувача в тексті повідомлення
                match = username_regex.search(text)
                if match:
                    mentioned_username = match.group(1)
                    mentioned_user_id = mentioned_username
                    mentioned_user_username = mentioned_username
                    
                    # Виконання SQL-запиту для отримання first_name та last_name за username
                    cursor.execute("SELECT first_name, last_name FROM users WHERE username=?", (mentioned_username,))
                    result = cursor.fetchone()
                    if result:
                        first_name, last_name = result
                        mentioned_user_first_name = first_name
                        mentioned_user_last_name = last_name



            #Перевірка частоти зміни карми одному учанику
            cursor.execute("SELECT date_time FROM karma_data WHERE user_id = ? AND mentioned_user_id = ? ORDER BY date_time DESC LIMIT 1", (user_id, mentioned_user_id))
            last_karma = cursor.fetchone()  # Отримати перший кортеж
            if last_karma:
                last_karma = int(last_karma[0])  # Отримати перший елемент цього кортежу
            
            
            # Перевірка, чи є записи в базі даних
            if last_karma:
                
                # Конвертування Unix timestamp у формат datetime
                last_date_time = datetime.utcfromtimestamp(last_karma)

                # Перевірка, чи минуло менше ніж 1 година з моменту останнього запису
                current_time = datetime.utcnow()
                time_difference = current_time - last_date_time
                print(current_time, last_date_time, time_difference)
                if time_difference < timedelta(hours=1): 
                    
                    reply_message = f"Не можна змінювати карму одному учаснику частіше ніж 1 раз на годину "
                    bot.reply_to(message, reply_message)
                    add_karma_to = False
                      
            if username != mentioned_username and add_karma_to == True:
                # Зберегти дані у БД
                sql = "INSERT INTO karma_data (date_time, user_id, user_username, user_first_name, user_last_name, mentioned_user_id, mentioned_user_username, mentioned_user_first_name, mentioned_user_last_name, post, add_karma) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                values = (message.date, user_id, username, first_name, last_name, mentioned_user_id, mentioned_user_username, mentioned_user_first_name, mentioned_user_last_name, text, karma_value)
                cursor.execute(sql, values)
                conn.commit()
               
                # Запит до БД: вибрати всі записи по полю mentioned_user_id та додати всі значення по полю add_karma
                cursor.execute("SELECT SUM(add_karma) FROM karma_data WHERE mentioned_user_id = ?", (mentioned_user_id,))
                total_karma = cursor.fetchone()[0]
                
                # Відправити повідомлення-реплай на зміну карми з клікабельним ідентифікатором користувача та сумою значень add_karma
                if karma_value == 1:
                    reply_message = f"Карма збільшилась до {total_karma}"
                else:
                    reply_message = f"Карма зменшилась до {total_karma}"
                bot.reply_to(message, reply_message)
            elif username == mentioned_username:
                reply_message = f"Не фроди! Хочеш підняти собі карму - задонать на ЗСУ!"
                bot.reply_to(message, reply_message)
                
    # Закрити підключення до БД
    cursor.close()
    conn.close()

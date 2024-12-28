import telebot
from telebot import types
import sqlite3
from datetime import datetime
import locale
import os

# Инициализация бота
bot = telebot.TeleBot('7654378121:AAEZ5IrR1tG0GnXJCtKddYuUrViexYfkeHo')

# Установка локали для корректного отображения дней недели
locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    if first_name is None:
        bot.send_message(message.chat.id, f'Привет, {last_name}. Это специальный бот для записи ко мне!💅')
    elif last_name is None:
        bot.send_message(message.chat.id, f'Привет, {first_name}. Это специальный бот для записи ко мне!💅')
    else:
        bot.send_message(message.chat.id, f'Привет, {first_name} {last_name}. Это специальный бот для записи ко мне!💅')
    
    # Показываем меню с inline-кнопками
    show_menu(message)

# Функция для отображения меню
def show_menu(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Записаться📅', callback_data='book')
    btn2 = types.InlineKeyboardButton('Отменить запись❌', callback_data='cancel')
    btn3 = types.InlineKeyboardButton('Недавние работы💅', callback_data='works')
    btn4 = types.InlineKeyboardButton('О мастере👩', callback_data='about')
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    bot.send_message(message.chat.id, 'Пожалуйста, выбери действие:', reply_markup=markup)

# Обработчик команды /admin
@bot.message_handler(commands=['admin'])
def admin(message):
    if (message.chat.id == 536796490) or (message.chat.id == 920281318):  # Проверка на админа
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Добавить запись', callback_data='insert_book')
        btn2 = types.InlineKeyboardButton('Удалить запись', callback_data='delete_book')
        btn3 = types.InlineKeyboardButton('Посмотреть клиентов', callback_data='view_clients')
        markup.row(btn1, btn2)
        markup.row(btn3)
        bot.send_message(message.chat.id, "Привет, Алина. Это твой любимый Рома. Выбери действие", reply_markup=markup)

# Обработчик callback-запросов
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == 'book':
        show_unique_dates(call.message)
    elif call.data == 'cancel':
        delete_booking(call.message)
    elif call.data == 'works':
        send_recent_works(call.message)  # Вызов функции для отправки изображений
    elif call.data == 'about':
        bot.send_message(call.message.chat.id, 'Я мастер маникюра Алина. Специализируюсь на Nude-маникюре. В среднем, время маникюра состовляет 2 часа.\
 В каждую свою работу я вкладываю душу и стараюсь, чтобы клиенту все понравилось. Буду рада с тобой познакомиться! Если остались какие-то вопросы, то вот мой телефон - +7(913)-087-37-66 или телеграм - @seongdi')
    elif call.data == 'insert_book':
        bot.send_message(call.message.chat.id, 'Хорошо, напиши дату(12.12.2024)')
        bot.register_next_step_handler(call.message, insert_book)
    elif call.data == 'delete_book':
        delete_book(call.message)
    elif call.data == 'view_clients':
        view_clients(call.message)
    elif call.data.startswith('select_date_'):
        handle_date_selection(call)
    elif call.data.startswith('select_time_'):
        handle_time_selection(call)

# Функция для отправки изображений и текста
def send_recent_works(message):
    # Отправляем текст
    bot.send_message(message.chat.id, 'Вот одни из моих последних работ. Такую же красоту я сделаю и тебе!')
    
    # Отправляем 4 изображения из папки static
    photo_folder = 'static'
    photo_files = ['photo1.jpg', 'photo2.jpg', 'photo3.jpg', 'photo4.jpg']
    
    for photo_file in photo_files:
        photo_path = os.path.join(photo_folder, photo_file)
        if os.path.exists(photo_path):
            with open(photo_path, 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
        else:
            bot.send_message(message.chat.id, f'Файл {photo_file} не найден.')

# Функция для отображения уникальных дат
def show_unique_dates(message):
    conn = sqlite3.connect('rte_nails.sql')
    cur = conn.cursor()
    
    # Выбираем только свободные окна (is_booked = 0)
    cur.execute("SELECT DISTINCT date FROM booking WHERE date >= DATE('now') AND is_booked = 0 ORDER BY date ASC")
    dates = cur.fetchall()

    cur.close()
    conn.close()

    if dates:
        markup = types.InlineKeyboardMarkup()
        for date in dates:
            date_obj = datetime.strptime(date[0], "%Y-%m-%d")
            day_of_week = date_obj.strftime('%a')
            formatted_date = f"{date_obj.strftime('%d.%m.%Y')}({day_of_week})"
            btn = types.InlineKeyboardButton(f"Дата: {formatted_date}", callback_data=f"select_date_{date[0]}")
            markup.add(btn)
        bot.send_message(message.chat.id, "Выберите дату для записи:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "К сожалению, свободных окошек для записи нет.")

# Обработчик выбора даты
def handle_date_selection(call):
    selected_date = call.data.split('_')[-1]

    conn = sqlite3.connect('rte_nails.sql')
    cur = conn.cursor()
    
    # Выбираем только свободные окна (is_booked = 0)
    cur.execute("SELECT id, time FROM booking WHERE date = ? AND is_booked = 0", (selected_date,))
    times = cur.fetchall()

    cur.close()
    conn.close()

    if times:
        markup = types.InlineKeyboardMarkup()
        for time in times:
            btn = types.InlineKeyboardButton(f"Время: {time[1]}", callback_data=f"select_time_{time[0]}")
            markup.add(btn)
        bot.send_message(call.message.chat.id, "Выберите время для записи:", reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "К сожалению, на эту дату свободных окошек нет.")

# Обработчик выбора времени
def handle_time_selection(call):
    booking_id = call.data.split('_')[-1]

    conn = sqlite3.connect('rte_nails.sql')
    cur = conn.cursor()
    
    # Проверяем, свободно ли окно
    cur.execute("SELECT date, time FROM booking WHERE id = ? AND is_booked = 0", (booking_id,))
    booking = cur.fetchone()

    if booking:
        date, time = booking
        # Помечаем окно как забронированное
        cur.execute("UPDATE booking SET is_booked = 1 WHERE id = ?", (booking_id,))
        conn.commit()
        bot.send_message(call.message.chat.id, f"Вы выбрали запись на {date} в {time}. Введите ваше имя для завершения записи.")
        bot.register_next_step_handler(call.message, user_name, booking_id)
    else:
        bot.send_message(call.message.chat.id, "Это окно уже занято. Пожалуйста, выберите другое.")

    cur.close()
    conn.close()

# Функция для получения имени пользователя
def user_name(message, booking_id):
    name = message.text.strip()
    bot.send_message(message.chat.id, 'Напишите свой контакт, по которому я смогу связаться с вами (например, номер телефона, телеграмм или ватсап).')
    bot.register_next_step_handler(message, user_contact, booking_id, name)

# Функция для получения контакта пользователя
def user_contact(message, booking_id, name):
    contact = message.text.strip()

    conn = sqlite3.connect('rte_nails.sql')
    cur = conn.cursor()
    
    cur.execute("SELECT date, time FROM booking WHERE id = ?", (booking_id,))
    booking = cur.fetchone()

    if booking:
        date, time = booking
        cur.execute("INSERT INTO users(user_id, name, contact, date, time) VALUES (?, ?, ?, ?, ?)", 
                    (message.chat.id, name, contact, date, time))
        conn.commit()
        bot.send_message(message.chat.id, f'Отлично! Вы записаны на {date} в {time}. Буду рада встрече.🙂')
    else:
        bot.send_message(message.chat.id, "Произошла ошибка. Пожалуйста, попробуйте снова.")

    cur.close()
    conn.close()

# Функция для добавления записи администратором
def insert_book(message):
    admin_date = message.text.strip()

    try:
        date_obj = datetime.strptime(admin_date, "%d.%m.%Y")
        formatted_date = date_obj.strftime("%Y-%m-%d")
        bot.send_message(message.chat.id, 'Напиши время(18:00)')
        bot.register_next_step_handler(message, adm_time, formatted_date)
    except ValueError:
        bot.send_message(message.chat.id, 'Неверный формат даты. Пожалуйста, введите дату в формате день.месяц.год, например 12.02.2025')
        bot.register_next_step_handler(message, insert_book)

# Функция для добавления времени администратором
def adm_time(message, formatted_date):
    admin_time = message.text.strip()
    conn = sqlite3.connect('rte_nails.sql')
    cur = conn.cursor()
    
    # Добавляем новое окно как свободное (is_booked = 0)
    cur.execute("INSERT INTO booking(date, time, is_booked) VALUES (?, ?, 0)", (formatted_date, admin_time))
    conn.commit()
    cur.close()
    conn.close()

    bot.send_message(message.chat.id, 'Отлично, добавил время')

# Функция для удаления записи администратором
def delete_book(message):
    conn = sqlite3.connect('rte_nails.sql')
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM booking WHERE date >= DATE('now')")
    rows = cur.fetchall()

    cur.close()
    conn.close()
    
    if rows:
        response = "Выбери ID записи:\n"
        for row in rows:
            response += f"ID: {row[0]}, Дата: {row[1]}, Время: {row[2]}\n"
    else:
        response = "Записей нет."

    bot.send_message(message.chat.id, response)
    bot.register_next_step_handler(message, del_book)

# Функция для удаления записи по ID
def del_book(message):
    book_id = message.text.strip()

    if not book_id.isdigit():
        # Если введено не число, просим ввести снова
        bot.send_message(message.chat.id, 'Цифру напиши емае')
        bot.register_next_step_handler(message, del_book)  # Ждем следующего сообщения
        return  # Прерываем выполнение функции
    try:
        conn = sqlite3.connect('rte_nails.sql')
        cur = conn.cursor()
        
        cur.execute("DELETE FROM booking WHERE id = ?", (book_id,))
        conn.commit()

        cur.close()
        conn.close()
        bot.send_message(message.chat.id, 'Отлично, удалил')
    
    except Exception as e:
        bot.send_message(message.chat.id, f'Произошла ошибка: {e}')

# Функция для просмотра клиентов администратором
def view_clients(message):
    conn = sqlite3.connect('rte_nails.sql')
    cur = conn.cursor()
    
    cur.execute("SELECT name, contact, date, time FROM users WHERE date >= DATE('now')")
    clients = cur.fetchall()

    cur.close()
    conn.close()

    if clients:
        response = "Список клиентов:\n"
        for client in clients:
            response += f"Имя: {client[0]}, Контакт: {client[1]}, Дата: {client[2]}, Время: {client[3]}\n"
    else:
        response = "Клиентов нет."

    bot.send_message(message.chat.id, response)

# Функция для удаления записи пользователем
def delete_booking(message):
    conn = sqlite3.connect('rte_nails.sql')
    cur = conn.cursor()
    
    # Получаем запись пользователя
    cur.execute("SELECT date, time FROM users WHERE user_id = ?", (message.chat.id,))
    booking = cur.fetchone()

    if booking:
        date, time = booking
        # Освобождаем окно
        cur.execute("UPDATE booking SET is_booked = 0 WHERE date = ? AND time = ?", (date, time))
        # Удаляем запись пользователя
        cur.execute("DELETE FROM users WHERE user_id = ?", (message.chat.id,))
        conn.commit()
        bot.send_message(message.chat.id, 'Ваша запись успешно удалена.')
    else:
        bot.send_message(message.chat.id, 'У вас нет активных записей.')

    cur.close()
    conn.close()

# Обработчик всех остальных сообщений
@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    show_menu(message)

# Запуск бота
bot.polling(none_stop=True)
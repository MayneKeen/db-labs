import telebot
from telebot import types
import configparser
import datetime
import logging
import db_interface
import re

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

API_TOKEN = config.get("bot", "API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
bot.skip_pending = True

db_interface = db_interface
db_cursor = db_interface.cursor

type_names = []
prod_name = ""
price = 0
type = ""
desc = ""
review_mark = 0
user_email = ""
user_id = ""
user_name = ""
user_phone = ""
auth_code = 777
prod_id = 0


@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.text == '/start':
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        button1 = types.KeyboardButton("Добавить товар")
        button2 = types.KeyboardButton("Изменить товар")
        button3 = types.KeyboardButton("Список производителей")
        button4 = types.KeyboardButton("Каталог")
        button5 = types.KeyboardButton("Список товаров")
        button6 = types.KeyboardButton("Добавить отзыв")
        button7 = types.KeyboardButton("Добавить клиента")
        button8 = types.KeyboardButton("Удалить отзыв")

        markup.add(button1, button2, button3, button4, button5, button6, button7, button8)

        bot.send_message(message.chat.id,
                         "Выберите пункт из меню.\n"
                         "Помощь: /help".format(message.from_user, bot.get_me()),
                         reply_markup=markup)


@bot.message_handler(regexp="Изменить товар")
def button(message):
    if message.text == 'Изменить товар':
        keyboard_for_editting = types.InlineKeyboardMarkup(row_width=1)
        key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')

        keyboard_for_editting.add(key_exit)

        msg = bot.send_message(message.chat.id, "Выберите имя товара", reply_markup=keyboard_for_editting)
        bot.register_next_step_handler(msg, ask_prod_name_edit)


def ask_prod_name_edit(message):
    global prod_name
    global prod_id
    exit_keyboard = types.InlineKeyboardMarkup(row_width=2)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)
    prod_name = message.text
    if not prod_name:
        msg = bot.send_message(message.chat.id, 'Напиши нормально и попробуй еще раз', reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_prod_name_edit)
        return

    pid = db_interface.get_prod_id_by_name(prod_name)

    if pid == 1:
        key_add = types.InlineKeyboardButton(text="Да", callback_data='add_while_edit')
        exit_keyboard.add(key_add)
        msg = bot.send_message(message.chat.id, 'Такого продукта нет в базе. \nЖелате добавить его?',
                               reply_markup=exit_keyboard)
        return

    prod_id = pid
    msg = bot.send_message(message.chat.id,
                           "Введите новое имя товара. Если его менять не нужно, введите старый вариант "
                           + prod_name, reply_markup=exit_keyboard)
    bot.register_next_step_handler(msg, edit_prod_name)


def edit_prod_name(message):
    global prod_name
    exit_keyboard = types.InlineKeyboardMarkup(row_width=2)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)
    prod_name = message.text
    if not prod_name:
        msg = bot.send_message(message.chat.id, 'Напиши нормально и попробуй еще раз', reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_prod_name_edit)
        return

    msg = bot.send_message(message.chat.id,
                           "Введите новую цену для товара. Если ее менять не нужно, введите старый вариант "
                           + prod_name, reply_markup=exit_keyboard)
    bot.register_next_step_handler(msg, ask_prod_price_edit)


def ask_prod_price_edit(message):
    global prod_name
    global price
    exit_keyboard = types.InlineKeyboardMarkup(row_width=2)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)
    price = int(message.text)

    if not price:  # or not price.isdigit():
        price = 0
        msg = bot.send_message(message.chat.id, 'Цифры писать разучился?', reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_prod_price_edit)
        return

    change_keyboard = types.InlineKeyboardMarkup(row_width=2)
    key_change = types.InlineKeyboardButton(text="Да", callback_data='change_desc')
    key_no_changes = types.InlineKeyboardButton(text="Нет", callback_data='no_changes_desc')
    change_keyboard.add(key_change, key_no_changes, key_exit)

    msg = bot.send_message(message.chat.id, "Нужно ли менять описание товара?", reply_markup=change_keyboard)
    return


def ask_prod_desc_edit(message):
    global desc
    exit_keyboard = types.InlineKeyboardMarkup(row_width=2)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)
    desc = message.text

    if not desc:
        desc = ""
        msg = bot.send_message(message.chat.id, 'Некорректное описание, попробуйте еще раз', reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_prod_desc_edit)
        return

    msg = bot.send_message(message.chat.id, 'Применяю изменения для товара ' + prod_name + '...')
    edit_prod(msg)


def edit_prod(message):
    global prod_name
    global price
    global desc
    global prod_id

    db_interface.refactor_product(prod_id, prod_name, price, desc)
    msg = bot.send_message(message.chat.id, 'Товар успешно изменен ' + prod_name)
    return


@bot.message_handler(regexp="Каталог")
def button(message):
    if message.text == 'Каталог':
        keyboard_for_catalog = types.InlineKeyboardMarkup(row_width=2)

        key_price = types.InlineKeyboardButton(text="По цене", callback_data='10')
        key_type = types.InlineKeyboardButton(text="По типу", callback_data='11')
        key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')

        keyboard_for_catalog.add(key_price, key_type, key_exit)

        bot.send_message(message.chat.id, "Выберите метод сортировки.", reply_markup=keyboard_for_catalog)


@bot.message_handler(regexp="Удалить отзыв")
def button(message):
    if message.text == 'Удалить отзыв':
        exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
        key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
        exit_keyboard.add(key_exit)

        msg = bot.send_message(message.chat.id, "Введите вашу электронную почту", reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_email_dr)


def ask_email_dr(message):
    global user_email
    emails = db_interface.get_emails()
    email = message.text
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)

    if email not in emails:
        msg = bot.send_message(message.chat.id, "Такой почты нет в базе, попробуйте еще раз",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_email_dr)
        return

    user_email = email
    reviews = db_interface.get_reviews_format(email)

    if reviews == -1:
        msg = bot.send_message(message.chat.id, "Похоже, у вас пока еще нет отзывов... "
                                                "\nЕсли Вы хотите попробовать другую почту -- введите ее"
                                                "\nЕсли нет, нажмите \'Отмена\'",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_email_dr)
        return

    if len(reviews) > 4096:
        for x in range(0, len(reviews), 4096):
            bot.send_message(message.chat.id, reviews[x:x + 4096])
    else:
        bot.send_message(message.chat.id, reviews)

    msg = bot.send_message(message.chat.id, "Введите идентификатор вашего отзыва", reply_markup=exit_keyboard)
    bot.register_next_step_handler(msg, ask_review_id_dr)


def ask_review_id_dr(message):
    global user_email
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)
    review_id = message.text
    reviews = db_interface.get_reviews_format(user_email)
    if not review_id or not review_id.isdigit() or review_id not in db_interface.get_review_ids_list(user_email):
        msg = bot.send_message(message.chat.id, "Некорректный идентификатор отзыва, попробуйте еще раз",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_review_id_dr)
        return
    msg = bot.send_message(message.chat.id, "Удаляю отзыв с индентификатором " + str(review_id) + "...")
    delete_review(msg, review_id)


def delete_review(message, review_id):
    db_interface.delete_review(review_id)
    bot.send_message(message.chat.id, "Удален отзыв " + review_id)
    return


@bot.message_handler(regexp="Добавить клиента")
def button(message):
    if message.text == 'Добавить клиента':
        exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
        key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
        exit_keyboard.add(key_exit)

        msg = bot.send_message(message.chat.id, "Как вас зовут?", reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_user_name)


def ask_user_name(message):
    global user_name
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)

    user_name = message.text
    if not user_name:
        msg = bot.send_message(message.chat.id, "Некорректное имя, введите еще раз", reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_user_name)
        return
    msg = bot.send_message(message.chat.id, "Введите e-mail", reply_markup=exit_keyboard)
    bot.register_next_step_handler(msg, ask_user_email)


def ask_user_email(message):
    global user_email
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)
    user_email = message.text

    pattern = r'\w+@[a-z]+\.[a-z]+'
    if not re.match(pattern, user_email):
        user_email = ""
        msg = bot.send_message(message.chat.id, "Некорректный e-mail, попробуйте еще раз", reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_user_email)
        return

    check = db_interface.check_mail(user_email)
    if check != 1:
        # user_email = ""
        # msg = bot.send_message(message.chat.id, "Такой e-mail уже зарегистрирован в базе, попробуйте еще раз",
        #                        reply_markup=exit_keyboard)
        # bot.register_next_step_handler(msg, ask_user_email)
        # return
        buyer_exists_keyboard = types.InlineKeyboardMarkup(row_width=2)
        key_true = types.InlineKeyboardButton(text="Добавить", callback_data='buyer_exists_add')
        key_false = types.InlineKeyboardButton(text="Не добавлять", callback_data='buyer_exists_dont_add')
        key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
        buyer_exists_keyboard.add(key_true, key_false, key_exit)

        msg = bot.send_message(message.chat.id, "Такой e-mail уже зарегистрирован в базе,"
                                                " желаете ли вы добавить сотрудника " + user_name + " с почтой " + user_email + "?",
                               reply_markup=buyer_exists_keyboard)
        return
    msg = bot.send_message(message.chat.id, "Введите только цифры вашего номера телефона", reply_markup=exit_keyboard)
    bot.register_next_step_handler(msg, ask_user_phone)


def ask_user_phone(message):
    global user_phone
    global user_name
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)
    user_phone = message.text

    if not user_phone.isdigit():
        user_phone = ""
        msg = bot.send_message(message.chat.id, "Некорректный номер, пожалуйста, вводите только цифры",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_user_phone)
        return

    check = db_interface.check_phone(user_phone)
    if check != 1:
        user_phone = ""
        msg = bot.send_message(message.chat.id, "Такой номер телефона уже зарегистрирован в базе, попробуйте еще раз",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_user_phone)
        return

    employee_register_keyboard = types.InlineKeyboardMarkup(row_width=2)
    key_true = types.InlineKeyboardButton(text="Да", callback_data='employee')
    key_false = types.InlineKeyboardButton(text="Нет", callback_data='not_employee')
    employee_register_keyboard.add(key_true, key_false)

    msg = bot.send_message(message.chat.id, "Регистрировать ли сотрудника " + user_name,
                           reply_markup=employee_register_keyboard)
    # bot.register_next_step_handler(msg, check_auth_code())


def check_auth_code(message):
    global auth_code
    continue_keyboard = types.InlineKeyboardMarkup(row_width=2)
    key_continue = types.InlineKeyboardButton(text="Да", callback_data='employee_retry')
    key_exit = types.InlineKeyboardButton(text="Нет", callback_data='exit')
    continue_keyboard.add(key_continue, key_exit)

    bot.delete_message(message.chat.id, message.message_id)
    if not int(message.text) == auth_code:
        msg = bot.send_message(message.chat.id, "Некорректный код доступа \n Желаете попробовать еще раз?",
                               reply_markup=continue_keyboard)
        bot.clear_reply_handlers_by_message_id(msg)
        bot.register_next_step_handler(msg, check_auth_code)
        return

    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)
    msg = bot.send_message(message.chat.id, "Введите даты начала-конца вашего договора в формате dd.mm.yyyy-dd.mm.yyyy"
                                            " с нулями",
                           reply_markup=exit_keyboard)
    bot.register_next_step_handler(msg, ask_dates)


def ask_dates(message):
    global user_name
    # date = datetime.date(year, month, day)
    dates = message.text
    pattern = r'\d\d\.\d\d\.\d\d\d\d\-\d\d\.\d\d\.\d\d\d\d'
    bot.clear_reply_handlers_by_message_id(message)
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)

    if not re.match(pattern, dates):

        msg = bot.send_message(message.chat.id,
                               "Некорректные даты. Корректный формат: dd.mm.yyyy-dd.mm.yyyy, нули учитываются"
                               " \n Попробуйте еще раз",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_dates)
        return

    dates_list = re.split(r'-', dates)

    start = re.split(r'\.', dates_list[0])
    end = re.split(r'\.', dates_list[1])
    start_year = int(start[2])
    start_month = int(start[1])
    start_day = int(start[0])
    end_year = int(end[2])
    end_month = int(end[1])
    end_day = int(end[0])

    if start_year > 3000 or end_year > 3000:
        max_year = max(start_year, end_year)

        msg = bot.send_message(message.chat.id,
                               "Пока мы все живем в 2021, " + user_name + " живет в " + str(max_year) +
                               " \n Попробуйте ввести год хотя бы меньше 3000",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_dates)
        return

    elif start_year < 1900 or end_year < 1900:
        min_year = min(start_year, end_year)

        msg = bot.send_message(message.chat.id,
                               "Пока мы все живем в 2021, " + user_name + " живет в " + str(min_year) +
                               " \n Попробуйте ввести год больше 1900",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_dates)
        return

    elif start_month > 12 or end_month > 12 or start_month < 1 or end_month < 1:
        msg = bot.send_message(message.chat.id,
                               "Если вы не знали, месяцы бывают от 1 до 12. \nПожалуйста ведите корректный месяц",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_dates)
        return

    elif start_day > 30 or end_day > 30 or start_day < 1 or end_day < 1:
        msg = bot.send_message(message.chat.id,
                               # "Ну да, лень было обрабатывать случаи когда 31 день",
                               "Если вы не знали, дни бывают от 1 до 30. \nПожалуйста ведите корректный день",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_dates)
        return

    elif start_month == 2 and start_day > 28 or end_month == 2 and end_day > 28:
        msg = bot.send_message(message.chat.id,
                               # "Ну да, лень было обрабатывать случаи когда 29 дней",
                               "Если вы не знали, в феврале дни бывают не больше 28. "
                               "\nПожалуйста ведите корректный день",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_dates)
        return

    start_date = datetime.date(start_year, start_month, start_day)
    end_date = datetime.date(end_year, end_month, end_day)

    db_interface.add_employee(user_name, user_phone, user_email, start_date, end_date)
    bot.send_message(message.chat.id, "Сотрудник " + user_name + " успешно добавлен в базу!")


@bot.message_handler(regexp="Добавить отзыв")
def button(message):
    global type_names
    if message.text == 'Добавить отзыв':
        exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
        key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
        exit_keyboard.add(key_exit)

        bot.send_message(message.chat.id, "Выберите тип товара", reply_markup=exit_keyboard)
        update_type_names()
        msg = bot.send_message(message.chat.id, "Доступные типы товаров: " + str(type_names))
        bot.register_next_step_handler(msg, ask_type_review)


def ask_type_review(message):
    global type
    global type_names
    update_type_names()
    type = message.text.lower()
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)
    if type not in type_names:
        msg = bot.send_message(message.chat.id, 'Некорректный тип товара, попробуйте еще раз',
                               reply_markup=exit_keyboard)
        bot.send_message(message.chat.id, "Доступные типы товаров: " + str(type_names))
        bot.register_next_step_handler(msg, ask_type_review)
        return
    else:
        msg = bot.send_message(message.chat.id, "Теперь выберите товар типа " + type + " из списка -- введите имя"
                               , reply_markup=exit_keyboard)
        prods = db_interface.get_products_by_type(type)
        if len(prods) > 4096:
            for x in range(0, len(prods), 4096):
                bot.send_message(message.chat.id, prods[x:x + 4096])
        else:
            bot.send_message(message.chat.id, prods)
        bot.register_next_step_handler(msg, ask_product)


def ask_product(message):
    global type
    global prod_name
    prods = db_interface.get_products_by_type(type)
    prod = message.text
    if prod not in prods:
        exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
        key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
        exit_keyboard.add(key_exit)
        msg = bot.send_message(message.chat.id, 'Некорректный товар, попробуйте еще раз', reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_product)
        return
    else:
        prod_name = prod
        keyboard_for_review = types.InlineKeyboardMarkup(row_width=1)

        key_one = types.InlineKeyboardButton(text="1", callback_data='111')
        key_two = types.InlineKeyboardButton(text="2", callback_data='112')
        key_three = types.InlineKeyboardButton(text="3", callback_data='113')
        key_four = types.InlineKeyboardButton(text="4", callback_data='114')
        key_five = types.InlineKeyboardButton(text="5", callback_data='115')
        key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')

        keyboard_for_review.add(key_one, key_two, key_three, key_four, key_five, key_exit)
        msg = bot.send_message(message.chat.id, "Поставьте оценку товару", reply_markup=keyboard_for_review)


def ask_email(message):
    global user_email
    user_email = message.text
    emails = db_interface.get_emails()
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)

    if user_email not in emails:
        msg = bot.send_message(message.chat.id, "Такой почты нет в базе, попробуйте еще раз :("
                               , reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_email)
        return
    else:
        global user_id
        user_id = db_interface.get_buyer_id_by_email(user_email)
        msg = bot.send_message(message.chat.id, "И последнее: напишите какой-нибудь текст обзора :)",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_review_text)


def ask_review_text(message):
    global user_id
    global prod_name
    global review_mark
    review_text = message.text
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)
    if not review_text:
        msg = bot.send_message(message.chat.id, "Слыш, нормально пиши пожалуйста", reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_review_text)
        return
    else:
        pid = db_interface.get_prod_id_by_name(prod_name)
        result = db_interface.add_review(user_id, pid, review_mark, review_text)
        if not result:
            bot.send_message(message.chat.id, "Что-то пошло не так, товар не добавлен :(")
            return
        else:
            bot.send_message(message.chat.id, "Отзыв добавлен")
            return


@bot.message_handler(regexp="Добавить товар")
def button(message):
    if message.text == 'Добавить товар':
        exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
        key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
        exit_keyboard.add(key_exit)
        msg = bot.send_message(message.chat.id, "Выберите имя товара.", reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_name)


def ask_name(message):
    global prod_name
    # bot.delete_message(message.chat.id, message.message_id)
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)
    prod_name = message.text
    if not prod_name:
        msg = bot.send_message(message.chat.id, 'Напиши нормально и попробуй еще раз', reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_name)
        return

    pid = db_interface.get_prod_id_by_name(prod_name)

    if not pid == 1:
        msg = bot.send_message(message.chat.id, 'Такой продукт уже есть в базе, попробуйте другое имя',
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_name)
        return

    msg = bot.send_message(message.chat.id, "Введите цену для нового товара " + prod_name, reply_markup=exit_keyboard)
    bot.register_next_step_handler(msg, ask_price)


def ask_price(message):
    global price
    global type_names
    price = message.text
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)

    if not price.isdigit():
        msg = bot.send_message(message.chat.id, 'Цифры писать разучился?', reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_price)
        return

    bot.send_message(message.chat.id, "Товар " + prod_name + " с ценой " + price + ". Какого типа этот товар?",
                     reply_markup=exit_keyboard)

    update_type_names()
    msg = bot.send_message(message.chat.id, "Доступные типы товаров: " + str(type_names))

    bot.register_next_step_handler(msg, ask_type)


def ask_type(message):
    global type
    global type_names
    update_type_names()
    type = message.text.lower()
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)

    if type not in type_names:
        msg = bot.send_message(message.chat.id, 'Некорректный тип товара, введите еще раз', reply_markup=exit_keyboard)
        bot.send_message(message.chat.id, "Доступные типы товаров: " + str(type_names))
        bot.register_next_step_handler(msg, ask_type)
        return
    msg = bot.send_message(message.chat.id, "Все задано корректно, какое у " + prod_name + " будет описание?",
                           reply_markup=exit_keyboard)
    bot.register_next_step_handler(msg, ask_desc)


def ask_desc(message):
    global desc
    desc = message.text
    if not desc:
        exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
        key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
        exit_keyboard.add(key_exit)

        msg = bot.send_message(message.chat.id, 'Некорректное описание, введите еще раз', reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_desc())
        return
    msg = bot.send_message(message.chat.id, "Все значения заданы корректно")
    if db_interface.add_product(prod_name, price, type, desc) == 1:
        msg = bot.send_message(message.chat.id, "Товар добавлен")
    else:
        msg = bot.send_message(message.chat.id, "Что-то пошло не так...")


@bot.message_handler(regexp="Список производителей")
def button(message):
    if message.text == 'Список производителей':
        manufacturers = db_interface.get_manufacturers()
        if len(manufacturers) > 4096:
            for x in range(0, len(manufacturers), 4096):
                bot.send_message(message.chat.id, manufacturers[x:x + 4096])
        else:
            bot.send_message(message.chat.id, manufacturers)


@bot.message_handler(regexp="Список товаров")
def button(message):
    if message.text == 'Список товаров':
        try:
            prods = db_interface.get_products()
            if len(prods) > 4096:
                for x in range(0, len(prods), 4096):
                    bot.send_message(message.chat.id, prods[x:x + 4096])
            else:
                bot.send_message(message.chat.id, prods)
        except telebot.apihelper.ApiTelegramException:
            bot.send_message(message.chat.id, "Ошибочка вышла")


@bot.message_handler(commands=['help'])
def help_message(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(telebot.types.InlineKeyboardButton(text='time', callback_data=1))
    markup.add(telebot.types.InlineKeyboardButton(text='help', callback_data=2))
    markup.add(telebot.types.InlineKeyboardButton(text='joke', callback_data=3))
    markup.add(telebot.types.InlineKeyboardButton(text='menu', callback_data=4))

    #     button1 = types.KeyboardButton("Добавить товар")
    #     button2 = types.KeyboardButton("Изменить товар")
    #     button3 = types.KeyboardButton("Список производителей")
    #     button4 = types.KeyboardButton("Каталог\n")
    #     button5 = types.KeyboardButton("Список товаров\n")
    #     button6 = types.KeyboardButton("Добавить отзыв\n")
    #     button7 = types.KeyboardButton("Добавить клиента\n")
    #     button8 = types.KeyboardButton("Удалить отзыв")

    commands = "\nДобавить товар\nИзменить товар\nСписок производителей\nКаталог" \
               "\nСписок товаров\nДобавить отзыв\nДобавить клиента\nУдалить отзыв"
    bot.send_message(message.chat.id, "Доступные команды:\n" + commands +
                     "\n\nЕсли Вы хотите добавить нового сотрудника, воспользуйтесь функцией \"Добавить клиента\"",
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    bot.answer_callback_query(callback_query_id=call.id, text='Вот доступные команды')
    answer = ''

    if call.data == 'exit':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        msg = bot.send_message(call.message.chat.id, "Действия отменены")
        bot.clear_step_handler_by_chat_id(msg.chat.id)
        return

    if call.data == '1':
        send_time(call.message)
        answer = 'Текущее время'
    elif call.data == '2':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        help_message(call.message)
    elif call.data == '3':
        bot.send_message(call.message.chat.id, text="Шел медведь по лесу, видит горящую машину. Сел в нее и сгорел.")
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if call.data == '4':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        send_welcome(call.message)

    # sorting commands next

    # price
    elif call.data == '10':
        keyboard_for_price_sort = types.InlineKeyboardMarkup(row_width=2)

        key_lower = types.InlineKeyboardButton(text="Дешевле", callback_data='21')
        key_higher = types.InlineKeyboardButton(text="Дороже", callback_data='22')
        keyboard_for_price_sort.add(key_lower, key_higher)

        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, "Сначала дешевле или дороже?", reply_markup=keyboard_for_price_sort)
    # type
    elif call.data == '11':
        update_type_names()
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        for name in type_names:
            keyboard.add(types.InlineKeyboardButton(text=name, callback_data=name))

        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, "Выберите тип продукта.", reply_markup=keyboard)

    # sorting options

    # by price -> lower first
    elif call.data == '21':
        prods = db_interface.get_products_by_price(1)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, "Сначала дешевле:")
        if len(prods) > 4096:
            for x in range(0, len(prods), 4096):
                bot.send_message(call.message.chat.id, prods[x:x + 4096])
        else:
            bot.send_message(call.message.chat.id, prods)

    # by price -> higher first
    elif call.data == '22':
        prods = db_interface.get_products_by_price(0)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, "Сначала дороже: ")
        if len(prods) > 4096:
            for x in range(0, len(prods), 4096):
                bot.send_message(call.message.chat.id, prods[x:x + 4096])
        else:
            bot.send_message(call.message.chat.id, prods)

    # sorting options options

    if call.data in type_names:
        prods = db_interface.get_products_by_type(call.data)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, "Продукты по заданному типу " + call.data + ":")
        if len(prods) > 4096:
            for x in range(0, len(prods), 4096):
                bot.send_message(call.message.chat.id, prods[x:x + 4096])
        else:
            bot.send_message(call.message.chat.id, prods)

    # review options

    global review_mark
    global user_email
    if call.data == '111':
        review_mark = 1
        msg = bot.send_message(call.message.chat.id,
                               "Жаль, что вам не понравилось :( \n Чтобы сохранить отзыв, введите вашу электронную почту")
        bot.register_next_step_handler(msg, ask_email)

    elif call.data == '112':
        review_mark = 2
        msg = bot.send_message(call.message.chat.id,
                               "Жаль, что вам не понравилось :( \n Чтобы сохранить отзыв, введите вашу электронную почту")
        bot.register_next_step_handler(msg, ask_email)

    elif call.data == '113':
        review_mark = 3
        msg = bot.send_message(call.message.chat.id,
                               "Жаль, что вам не понравилось :( \n Чтобы сохранить отзыв, введите вашу электронную почту")
        bot.register_next_step_handler(msg, ask_email)

    elif call.data == '114':
        review_mark = 4
        msg = bot.send_message(call.message.chat.id,
                               "Рады, что вам понравилось! \n Чтобы сохранить отзыв, введите вашу электронную почту")
        bot.register_next_step_handler(msg, ask_email)
    elif call.data == '115':
        review_mark = 5
        msg = bot.send_message(call.message.chat.id,
                               "Рады, что вам понравилось! \n Чтобы сохранить отзыв, введите вашу электронную почту")
        bot.register_next_step_handler(msg, ask_email)

    if call.data == 'employee':
        msg = bot.send_message(call.message.chat.id, "Введите код доступа")
        bot.register_next_step_handler(msg, check_auth_code)

    elif call.data == 'not_employee':
        db_interface.add_buyer(user_name, user_phone, user_email)
        msg = bot.send_message(call.message.chat.id, "Клиент " + user_name + " успешно добавлен!")

    if call.data == 'employee_retry':
        bot.clear_reply_handlers_by_message_id(call.message.message_id)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        msg = bot.send_message(call.message.chat.id, "Попробуйте ввести код еще раз")
        bot.register_next_step_handler(msg, check_auth_code)

    if call.data == 'add_while_edit':
        bot.clear_reply_handlers_by_message_id(call.message.message_id)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        msg = bot.send_message(call.message.chat.id, "Добавляем товар " + prod_name + ".\nВведите цену.")
        bot.register_next_step_handler(msg, ask_price)

    if call.data == 'change_desc':
        bot.clear_reply_handlers_by_message_id(call.message.message_id)
        msg = bot.send_message(call.message.chat.id, "Введите обновленное описание для товара " + prod_name)
        bot.register_next_step_handler(msg, ask_prod_desc_edit)

    elif call.data == 'no_changes_desc':
        global desc
        desc = None
        bot.clear_reply_handlers_by_message_id(call.message.message_id)
        msg = bot.send_message(call.message.chat.id, "Применяем изменения к товару " + prod_name + "...")
        edit_prod(msg)

    if call.data == 'buyer_exists_add':
        bot.clear_reply_handlers_by_message_id(call.message.message_id)
        msg = bot.send_message(call.message.chat.id, "Введите код доступа")
        bot.register_next_step_handler(msg, check_auth_code)

    elif call.data == 'buyer_exists_dont_add':
        bot.clear_reply_handlers_by_message_id(call.message.message_id)
        msg = bot.send_message(call.message.chat.id, "Введите другой email")
        bot.register_next_step_handler(msg, ask_user_email)


@bot.message_handler(commands=['time'])
def send_time(message):
    bot.send_message(message.chat.id, datetime.datetime.today())
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text.lower() == 'привет':
        keyboard = types.InlineKeyboardMarkup()
        url_button = types.InlineKeyboardButton(text="Связаться с разработчиком", url="t.me/maynekeen/")
        keyboard.add(url_button)
        bot.send_message(message.chat.id, 'Привет! \n Чтобы узнать, что я могу, нажмите на /help',
                         reply_markup=keyboard)
    else:
        keyboard = types.InlineKeyboardMarkup()
        url_button = types.InlineKeyboardButton(text="Связаться с разработчиком", url="t.me/maynekeen/")
        keyboard.add(url_button)
        bot.send_message(message.chat.id, 'Не понимаю вас :(', reply_markup=keyboard)


def update_type_names():
    global type_names
    type_names = db_interface.get_type_names()


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)

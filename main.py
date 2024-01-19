import telebot
from telebot import types
from google_check import DatatoSheet
from google_check import check_availability

# Замените 'YOUR_BOT_TOKEN' на фактический токен вашего бота
bot = telebot.TeleBot('6875029749:AAFTueaD-JvNcPMXQXCryILSwQLNKI8jYrw')

length_prices = {
    "До плеч (30-35 см)": 2500,
    "Ниже плеч (40-45 см)": 3000,
    "Лопатки (50-55 см)": 3500,
    "Талия (60-65 см)": 4000,
    "Пояс (70-75 см)": 4500,
}

density_prices = {
    "Негустые (до 6 см)": 0,
    "Средняя густота (7-8 см)": 500,
    "Густые (от 9 см)": 1000,
    "Подложка": 1000
}

user_choices = {}

choisen_day = ""
user_data = {}
free_days = []



#Обработка команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    #Получая команду, бот высылает следующую функцию
    send_menu(message.chat.id)

#Главное меня бота
def send_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    #2 кнопки при нажатии которые действует соответсвующий функционал
    info_button = types.KeyboardButton("Информация")
    book_button = types.KeyboardButton("Рассчитать стоимость")
    markup.add(info_button, book_button)

    bot.send_message(chat_id, "Выберите действие:", reply_markup=markup)

#Функция для заполнения данных в Гугл таблицу
def confirm(message):
     bot.send_message(message.chat.id, "Данные успешно внесены")
     DatatoSheet(user_data, choisen_day)

#Главный обработчик сообщений, позволяет считывать текст, который написал пользователь, чтобы вызвать соответсвующий метод
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    chat_id = message.chat.id

    #Вызывая функцию посылает информацию о "создателе"
    if message.text == "Информация":
        send_info(chat_id)
    #Вызывает функцию для рассчета стоимости
    elif message.text == "Рассчитать стоимость":
        send_hair_length_menu(chat_id)
    #Возвращает в главное меню
    elif message.text == "Вернуться назад":
        send_menu(chat_id)
    #Проверяет сообщение от пользователя на содержание в словаре
    elif message.text in length_prices:
        user_choices[message.chat.id] = length_prices[message.text]
        send_hair_density_menu(chat_id)
    #Проверяет сообщение от пользователя на содержание в словаре
    elif message.text in density_prices:
        user_choices[message.chat.id] += density_prices[message.text]
        calculate_and_send_total(chat_id)
        ask_for_booking(chat_id)
    #Отправляет свободные дни для записи
    elif message.text == "Сделать запись":
        send_free_days(chat_id)
    elif message.text == "Не хочу записываться":
        bot.send_message(chat_id, "Спасибо за использование наших услуг!")
    elif message.text in free_days:
        global choisen_day
        choisen_day = message.text
        # Добавляем запрос данных пользователя
        bot.send_message(message.chat.id, "Введите ваше имя:")
        bot.register_next_step_handler(message, handle_name_input)
    elif message.text == "Все правильно":
        bot.send_message(message.chat.id, "Вы успешно записаны")
        confirm(message)
    elif message.text == "Заполнить заново":
        send_free_days(chat_id)
    else:
        bot.send_message(chat_id, "Некорректный выбор. Пожалуйста, используйте клавиатуру для выбора.")

#Функции для обработки данных от пользователя
def handle_name_input(message):
    user_data["name"] = message.text

    # Запрашиваем номер телефона
    bot.send_message(message.chat.id, "Введите ваш номер телефона:")
    bot.register_next_step_handler(message, handle_phone_input)


def handle_phone_input(message):
    user_data["phone"] = message.text

    # Запрашиваем соцсеть
    bot.send_message(message.chat.id, "Введите вашу соцсеть для связи:")
    bot.register_next_step_handler(message, handle_social_input)


def handle_social_input(message):
    user_data["social"] = message.text

    # Формируем сообщение для проверки
    check_message = f"Выбранный день: {choisen_day}\n" \
                    f"Обращаться к Вам: {user_data.get('name')}\n" \
                    f"Ваш номер телефона: {user_data.get('phone')}\n" \
                    f"Соцсеть для связи: {user_data.get('social')}\n" \
                    "Проверьте, все ли правильно?"

    # Отправляем сообщение для проверки
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    correct_button = types.KeyboardButton("Все правильно")



    redo_button = types.KeyboardButton("Заполнить заново")
    markup.add(correct_button, redo_button)

    bot.send_message(message.chat.id, check_message, reply_markup=markup)


# Добавляем обработчик для проверки данных
@bot.message_handler(func=lambda message: message.text in ["Все правильно", "Заполнить заново"])
def handle_check(message):
    if message.text == "Все правильно":
        bot.send_message(message.chat.id, "Спасибо за запись! Ожидайте подтверждение.")
    else:
        bot.send_message(message.chat.id, "Пожалуйста, заполните данные заново.")
        # Запускаем процесс ввода данных заново
        send_free_days(message.chat.id)

#Функция отправляет свободные дни для записи
def send_free_days(chat_id):
    global free_days
    #В список поступает значение свободных дней из функции, которая записана в файле google_check.py
    free_days = check_availability()
    if free_days:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        for day in free_days:
            markup.add(types.KeyboardButton(day))

        markup.add(types.KeyboardButton("Вернуться назад"))

        bot.send_message(chat_id, "Выберите свободный день:", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Нет свободных дней.")

#Спрашивает пользователя нужно ли записывать его
def ask_for_booking(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    book_button = types.KeyboardButton("Сделать запись")
    back_button = types.KeyboardButton("Вернуться назад")
    markup.add(book_button, back_button)
    bot.send_message(chat_id, "Записать Вас?", reply_markup=markup)


def send_info(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_button = types.KeyboardButton("Вернуться назад")
    markup.add(back_button)

    bot.send_message(chat_id, "ФИО: Мария Хаддадин\nНомер телефона: +123456789\nАдрес: ул. Маерчака, 16, центральный вход, 4 этаж, офис 408",
                     reply_markup=markup)


def send_hair_length_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for option in length_prices.keys():
        markup.add(types.KeyboardButton(option))

    markup.add(types.KeyboardButton("Вернуться назад"))

    bot.send_message(chat_id, "Выберите длину волос:", reply_markup=markup)


def send_hair_density_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for option in density_prices.keys():
        markup.add(types.KeyboardButton(option))

    markup.add(types.KeyboardButton("Вернуться назад"))

    bot.send_message(chat_id, "Выберите густоту волос:", reply_markup=markup)

#Считает полную стоимость услуги
def calculate_and_send_total(chat_id):
    total_price = user_choices.get(chat_id, 0)
    bot.send_message(chat_id, f"Итого: {total_price}₽")


@bot.message_handler(func=lambda message: message.text in density_prices)
def handle_hair_density_choice(message):
    chat_id = message.chat.id
    user_choices[chat_id] += density_prices[message.text]
    calculate_and_send_total(chat_id)


if __name__ == "__main__":
    bot.polling(none_stop=True)

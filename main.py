import telebot
from telebot import types
import random
import datetime

bot = telebot.TeleBot('')
users_list = []
IsStart = False
k = 0
n = k
IsGroup = False
Time_counter = False

def questions(category):
    if category == 'adult':
        QUESTIONS_FILE = open('adult.txt', encoding = 'utf-8')
        QUESTIONS = [i[:-1] for i in QUESTIONS_FILE.readlines()]
        QUESTIONS_FILE.close()
    elif category == 'main':
        QUESTIONS_FILE = open('main.txt', encoding='utf-8')
        QUESTIONS = [i[:-1] for i in QUESTIONS_FILE.readlines()]
        QUESTIONS_FILE.close()

    return QUESTIONS


def send_question(users_list, is_skip, send_name):
    global k
    global last_user_name
    global n
    user_name = users_list[k % (len(users_list))]
    print(f'Слудующий вопрос для {user_name}')
    if k == n:
        last_user_name = user_name
        question_number = k
        n = None
        return f'Вопрос для {user_name}' + '\n' + str(question_number) + '. ' + QUESTIONS[question_number]
    else:
        k+=1
        last_user_name = user_name
        question_number = k
        return f'Вопрос для {user_name}' + '\n' + str(question_number) + '. ' + QUESTIONS[question_number]


def send_message_quest(call, is_skip, users_list):
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton(text='Вопрос', callback_data='Вопрос')
    item2 = types.InlineKeyboardButton(text='Скип', callback_data='skip')
    markup.add(item1, item2)
    bot.send_message(call.message.chat.id, send_question(users_list, is_skip, call.from_user.first_name),
                     reply_markup=markup)



@bot.message_handler(commands=['start'])
def start(message):
    global IsStart
    IsStart = True
    bot.send_message(message.chat.id, 'Начало игры, чтобы войти в игру напишите /join')
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton(text = '18+', callback_data='adult')
    item2 = types.InlineKeyboardButton(text = 'Общие', callback_data='main')
    markup.add(item1, item2)
    bot.send_message(message.chat.id, 'Выберите режим игры', reply_markup=markup)


@bot.message_handler(commands=['join'])
def join(message):
    if IsStart:
        if IsGroup:
            if message.from_user.first_name not in users_list:
                users_list.append(message.from_user.first_name)
                bot.send_message(message.chat.id, message.from_user.first_name + ' вошел(ла) в игру!' + '\n' +
                                 ', '.join(users_list) + ' уже в игре')
            else:
                bot.send_message(message.chat.id, message.from_user.first_name + ' уже в игре')
            if len(users_list) == 1:
                markup = types.InlineKeyboardMarkup()
                item1 = types.InlineKeyboardButton(text='Вопрос', callback_data='Вопрос')
                markup.add(item1)
                bot.send_message(message.chat.id, 'Достаточное кол-во игроков! начало игры!', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'Выберите режим игры!')

    else:
        bot.send_message(message.chat.id, 'Начните игру!')


@bot.message_handler(commands=['leave'])
def player_leave(message):
    global IsStart
    global IsGroup
    if message.from_user.first_name in users_list:
        if IsStart:
            bot.send_message(message.chat.id, message.from_user.first_name + ' вышел из игры')
            users_list.remove(message.from_user.first_name)
            if len(users_list) == 0:
                IsStart = False
                IsGroup = False
                bot.send_message(message.chat.id, 'Недостаточно игроков, игра окончена')
        else:
            bot.send_message(message.chat.id, 'Игра ещё не началась')
    if (IsStart and not IsGroup) or (IsStart and IsGroup and len(users_list) == 0):
        bot.send_message(message.chat.id, 'Выход из игры')
        IsStart = False
        IsGroup = False


@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    global is_skip
    global QUESTIONS
    global IsGroup

    if call.data == 'Вопрос':
        if users_list != []:
            is_skip = False
            send_message_quest(call, is_skip, users_list)
        else:
            bot.send_message(call.message.chat.id, 'Недостаточно игроков!')

    if call.data == 'skip':
        is_skip = True
        send_message_quest(call, is_skip, users_list)

    if call.data == 'adult':
        if not IsGroup:
            if IsStart:
                QUESTIONS = questions('adult')
                IsGroup = True
                bot.send_message(call.message.chat.id, 'Выбран режим игры <b>18+</b>', parse_mode='html')
            else:
                bot.send_message(call.message.chat.id, 'Начните игру!')
            print(len(QUESTIONS))
        else:
            bot.send_message(call.message.chat.id, 'Режим уже выбран')

    if call.data == 'main':
        if not IsGroup:
            if IsStart:
                QUESTIONS = questions('main')
                IsGroup = True
                bot.send_message(call.message.chat.id, 'Выбран режим игры <b>Общий</b>', parse_mode='html')
            else:
                bot.send_message(call.message.chat.id, 'Начните игру!')
        else:
            bot.send_message(call.message.chat.id, 'Режим уже выбран')

@bot.message_handler()
def Timer_wait(message):
    global Time_counter
    global IsStart
    global IsGroup
    global users_list
    global last_Time
    if IsStart:
        new_Time = round(datetime.datetime.now().timestamp())
        if Time_counter:
            if new_Time - last_Time >= 7200:
                bot.send_message(message.chat.id, 'Прошло много времени, окончание игры, для начала пропишите /start')
                IsStart = False
                IsGroup = False
                users_list = []
                last_Time = new_Time
        else:
            last_Time = new_Time
            Time_counter = True

bot.polling(none_stop=True)

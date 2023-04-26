import Data
import Class_keyboard
import telebot
import asyncio
import slqite
import Some_def
import pyowm
import Class_enumeration
from Class_enumeration import enumeration
from telebot import types
from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker
from pyowm.commons.exceptions import NotFoundError

bot = telebot.TeleBot(Data.token_to_api)
gender = ''

#Bugs
#1) Обратка шага назад, дает 3 шага назад.
#2) Нужно разделить метод смены пола, на регистрацию и на изменение
#3) Изменение пола и города, должны записывать новые значения в бд

@bot.message_handler(commands=['start'])
def start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True);
    answer = f'Здравствуйте, меня зовут Weather_Bot. Я помогу вам подобрать одежду под сегодняшнюю погоду. Вы готовы начать?'
    bot.send_message(message.from_user.id, answer, reply_markup=markup);
    Data.actual_status = enumeration.wait_str
@bot.message_handler(content_types=['text'])
def get_text(message):
    if Data.actual_status == enumeration.wait_str:
        if message.text.lower() == 'да':
            check = Some_def.check_user_id(message.from_user.id, session)
            if check == True:
                keyboard = Class_keyboard.Keyboard()
                keyboard.add_button('Получить свежий прогноз погоды', 'weather')
                keyboard.add_button('Изменить данные', 'new_data')
                keyboard.add_button('Добавить одежду', 'add')
                bot.send_message(message.from_user.id,
                                 'Вот что я могу вам предложить',
                                 reply_markup=keyboard.get_keyboard())
                Data.actual_status = enumeration.wait_button
            else:
                bot.send_message(message.from_user.id, 'Вы для нас новый дорогой пользователь, пройдите пожалуйста небольшую регистрацию')
                bot.send_message(message.from_user.id, 'Укажите ваш пол')
                new_user = slqite.User()
                new_user.set_id(message.from_user.id)
                bot.register_next_step_handler(message, get_gender, new_user)
                Data.actual_status = enumeration.regist

        else:
            bot.send_message(message.from_user.id, 'Я не понимаю вас')

def get_gender(message, new_user):
    if Data.actual_status == enumeration.regist:
        right_ver = list['м','ж','муж','жен','мужской','женский']
        new_user.set_gender(message.text)
        bot.send_message(message.chat.id, 'Для лучшей работы, мне нужно получить вашу геолокацию')
        bot.send_message(message.chat.id, 'Укажите город в котором вы находитесь')
        bot.register_next_step_handler(message, get_new_city, new_user)
def get_new_city(message, new_user: slqite.User):
    if Data.actual_status == enumeration.regist:
        new_user.set_city(message.text)
        keyboard = Class_keyboard.Keyboard()
        keyboard.add_button('Получить прогноз погоды', 'weather')
        keyboard.add_button('Добавить одежду', 'add')
        bot.send_message(message.from_user.id,
                         'Запомнил вас',
                         reply_markup=keyboard.get_keyboard())
        session.add(new_user)
        session.commit()
        del new_user
        Data.actual_status = enumeration.wait_button
        del keyboard

def get_city(message):
    if Data.actual_status == enumeration.wait_str:
        Data.city = message.text
        keyboard = Class_keyboard.Keyboard()
        keyboard.add_button('Получить прогноз погоды', 'weather')
        keyboard.add_button('Добавить одежду', 'add')
        bot.send_message(message.from_user.id,
                         'Запомнил',
                         reply_markup=keyboard.get_keyboard())
        Data.actual_status = enumeration.wait_button
        del keyboard

#Здесь распологаются кнопки
@bot.callback_query_handler(func= lambda call:True)
def callback_add_or_prep(call):
    if Data.actual_status == enumeration.wait_button:
        if call.data == 'add':
            bot.send_message(call.message.chat.id, 'Здесь будет функция добавления')
            Data.actual_status = enumeration.time_to_add_clothes
            keyboard = Class_keyboard.Keyboard()
            keyboard.add_button('Назад', 'back')
            bot.send_message(call.message.chat.id, 'Сейчас вы можете вернуться на один шаг назад',
                             reply_markup=keyboard.get_keyboard())
            Data.actual_status = enumeration.wait_button
            del keyboard

        elif call.data == 'prep':
            bot.send_message(call.message.chat.id, 'Для лучшей работы, мне нужно получить вашу геолокацию.')
            bot.send_message(call.message.chat.id, 'Укажите город в котором вы находитесь')
            bot.register_next_step_handler(call.message, get_city)
            Data.actual_status = enumeration.wait_str

        elif call.data == 'new_city':
            bot.send_message(call.message.chat.id, 'Укажите город в котором вы находитесь')
            bot.register_next_step_handler(call.message, get_city)
            Data.actual_status = enumeration.wait_str

        elif call.data == 'weather':
            try:
                user = Some_def.get_user_by_id(call.message.chat.id, session)
                observation = Data.owm.weather_manager().weather_at_place(user.get_city())
                w = observation.weather
                temp = w.temperature('celsius')['temp']
                answer = f'Сегодня днем температура {temp} °C'
                keyboard = Class_keyboard.Keyboard()
                keyboard.add_button('Получить свежий прогноз погоды', 'weather')
                keyboard.add_button('Изменить данные', 'new_data')
                keyboard.add_button('Добавить одежду', 'add')
                bot.send_message(call.message.chat.id, answer, reply_markup=keyboard.get_keyboard())
                Data.actual_status = enumeration.wait_button
                del keyboard
            except NotFoundError as e:
                answer = f'Что то пошло не так. Попробуйте снова написать "/start".'
                bot.send_message(call.message.chat.id, answer)
        elif call.data == 'back':
            bot.send_message(call.message.chat.id, 'Укажите пожалуйста ваш пол')
            bot.register_next_step_handler(call.message, get_gender)
            Data.actual_status = enumeration.wait_str

        elif call.data == 'new_data':
            keyboard = Class_keyboard.Keyboard()
            keyboard.add_button('Город', 'new_city')
            keyboard.add_button('Пол', 'gender')
            bot.send_message(call.message.chat.id, 'Что вы хотите изменить?', reply_markup=keyboard.get_keyboard())
            Data.actual_status = enumeration.wait_button
            del keyboard

        elif call.data == 'gender':
            bot.send_message(call.message.chat.id, 'Укажите пожалуйста ваш пол')
            bot.register_next_step_handler(call.message, get_gender)
            Data.actual_status = enumeration.wait_str


async def main():
    engine = slqite.connect_to_DB()
    Session = sessionmaker(bind=engine)
    global session
    session = Session()
    while True:
        try:
            await bot.polling(none_stop=True, interval=0)
        except Exception as e:
            print(e)
            await asyncio.sleep(5)

if __name__ == '__main__':
    asyncio.run(main())
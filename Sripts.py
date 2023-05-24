import io
import requests
import sqlalchemy
import Data
import Class_keyboard
import telebot
import asyncio
import slqite
import Some_def
import pyowm
import Class_enumeration
import Models_TF
import tensorflow as tf
from slqite import User, Clothes
from PIL import Image
from tensorflow.keras.models import load_model
from Class_enumeration import enumeration
from telebot import types
from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker
from pyowm.commons.exceptions import NotFoundError
from io import BufferedWriter, FileIO


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
                bot.register_next_step_handler(message, get_new_gender, new_user)
                Data.actual_status = enumeration.regist

        else:
            bot.send_message(message.from_user.id, 'Я не понимаю вас')
    else:
        keyboard = Class_keyboard.Keyboard()
        keyboard.add_button('Да', 'help_user_yes')
        keyboard.add_button('нет', 'help_user_no')
        bot.send_message(message.from_user.id,'Похоже, что сейчас я ожидаю другое действие, вам нужна помощь?',
                         reply_markup=keyboard.get_keyboard())


def get_gender(message, new_user):
    if Data.actual_status == enumeration.wait_str:
        right_ver = list['м','ж','муж','жен','мужской','женский']
        new_user.set_gender(message.text)
        bot.send_message(message.chat.id, 'Изменения внесены')
def get_new_gender(message, new_user):
    if Data.actual_status == enumeration.regist:
        right_ver = list['м', 'ж', 'муж', 'жен', 'мужской', 'женский']
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
        session.query(User).filter(User.id==message.from_user.id).update({'city': Data.city})
        keyboard = Class_keyboard.Keyboard()
        keyboard.add_button('Получить прогноз погоды', 'weather')
        keyboard.add_button('Добавить одежду', 'add')
        bot.send_message(message.from_user.id,
                         'Запомнил',
                         reply_markup=keyboard.get_keyboard())
        Data.actual_status = enumeration.wait_button
        del keyboard

@bot.message_handler(content_types= 'photo')
def handle_photo(message):
    if Data.actual_status == enumeration.time_to_add_clothes:
        file_info = bot.get_file(message.photo[-1].file_id)
        file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(Data.token_to_api, file_info.file_path))
        src = 'photo/'+ str(message.date) + '.jpg'
        try:
            with open(src, 'wb') as new_file:
                buffer = io.BufferedWriter(new_file)
                buffer.write(file.content)
                buffer.close()
        except BaseException as e:
            print(e)
        print(type(file.content))
        image = Image.open(src)
        prediction = Models_TF.predict(model, image)
        if prediction:
            print(prediction)
            new_photo = slqite.Clothes()
            new_photo.set_type(prediction)
            new_photo.set_user_id(message.from_user.id)
            new_photo.set_file_name(src)
            session.add(new_photo)
            session.commit()
            del new_photo
            keyboard = Class_keyboard.Keyboard()
            keyboard.add_button('Добавить еще одну одежду', 'add')
            keyboard.add_button('Получить прогноз погоды', 'weather')
            bot.send_message(message.from_user.id, 'Записал', reply_markup=keyboard.get_keyboard())
            Data.actual_status = enumeration.wait_button
        else:
            keyboard = Class_keyboard.Keyboard()
            keyboard.add_button('Добавить еще одну одежду', 'add')
            keyboard.add_button('Получить прогноз погоды', 'weather')
            bot.send_message(message.from_user.id, 'Что-то пошло не так. Попробуйте еще раз отправить фотографию.'
                                                   'Если не получится, то сделайте фотографию на более контрастном фоне.'
                                                   'Например: Если футболка черная, то на белом фоне', reply_markup=keyboard.get_keyboard())
            Data.actual_status = enumeration.wait_button

#Здесь распологаются кнопки
@bot.callback_query_handler(func= lambda call:True)
def callback_add_or_prep(call):
    if call.data == 'help_user_yes':
        str = enumeration.new_dict[Data.actual_status]
        bot.send_message(call.message.chat.id, str)
    if call.data == 'help_user_no':
        bot.send_message(call.message.chat.id, 'Хорошо, не отвлекаю')
    if Data.actual_status == enumeration.wait_button:
        if call.data == 'add':
            bot.send_message(call.message.chat.id, 'Жду фотографию')
            Data.actual_status = enumeration.time_to_add_clothes
            bot.register_next_step_handler(call.message, handle_photo)

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
                #Отправка фото
                clothes_1, clothes_2 = slqite.get_clothes(session,call.message.chat.id,temp)
                if clothes_1 and clothes_2:
                    photo1 = Image.open(clothes_1)
                    photo2 = Image.open(clothes_2)
                    bot.send_photo(call.message.chat.id, photo1)
                    bot.send_photo(call.message.chat.id, photo2)
                elif clothes_1:
                    photo = Image.open(clothes_1)
                    bot.send_photo(call.message.chat.id, photo)
                    answer = f'У меня в базе данных нету одежды. Тип = низ'
                    bot.send_message(call.message.chat.id, answer)
                    answer = f'Советую вам добавить несколько вариантов'
                    bot.send_message(call.message.chat.id, answer)
                elif clothes_2:
                    photo = Image.open(clothes_2)
                    bot.send_photo(call.message.chat.id, photo)
                    answer = f'У меня в базе данных нету одежды. Тип = верх'
                    bot.send_message(call.message.chat.id, answer)
                    answer = f'Советую вам добавить несколько вариантов'
                    bot.send_message(call.message.chat.id, answer)
                else:
                    answer = f'Я не нашел одежду в моей базе данных. Тип = верх, низ'
                    bot.send_message(call.message.chat.id, answer)
                    answer = f'Советую вам добавить несколько вариантов'
                    bot.send_message(call.message.chat.id, answer)
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
            keyboard.add_button('Город', 'city')
            keyboard.add_button('Пол', 'gender')
            bot.send_message(call.message.chat.id, 'Что вы хотите изменить?', reply_markup=keyboard.get_keyboard())
            Data.actual_status = enumeration.wait_button
            del keyboard

        elif call.data == 'gender':
            bot.send_message(call.message.chat.id, 'Укажите пожалуйста ваш пол')
            bot.register_next_step_handler(call.message, get_gender)
            Data.actual_status = enumeration.wait_str

        elif call.data == 'city':
            bot.send_message(call.message.chat.id, 'Укажите пожалуйста ваш город')
            bot.register_next_step_handler(call.message, get_city)
            Data.actual_status = enumeration.wait_str
    else:
        keyboard = Class_keyboard.Keyboard()
        keyboard.add_button('Да', 'help_user_yes')
        keyboard.add_button('нет', 'help_user_no')
        bot.send_message(call.message.chat.id,'Похоже, что сейчас я ожидаю другое действие, вам нужна помощь?',
                         reply_markup=keyboard.get_keyboard())

async def main():
    engine = slqite.connect_to_DB()
    Session = sessionmaker(bind=engine)
    global model
    model = Models_TF.load_or_create_model_tf()
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
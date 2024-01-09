import time
import telebot
# import pandas as pd
# import numpy as np
from confBOT import api_key, api_secret
import requests
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import myMath
import datetime
from Secret import token # в данном файле находится token бота(создать Secret.py и прописать: token = 'your token')


client = Client(api_key, api_secret)
mybot = telebot.TeleBot(token)
token_info = {} # Слварь с даными о стоимости крипты


def get_price_token(): # Фун-ия для записи данных о стоимости крипты с биржы Binance
    with open('token.txt', 'w', encoding='UTF-8') as file:
        prices = client.get_all_tickers()
        for i in prices:
            if 'USDT' in i['symbol'][-4:]:
                token_info[i['symbol']] = i['price'].rstrip('0')
        file.write(str(token_info))


@mybot.message_handler(commands=['start'])
def start_mess(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    brn1 = telebot.types.KeyboardButton('Курсы валют')
    brn2 = telebot.types.KeyboardButton('Крипта')
    markup.add(brn1, brn2)
    mybot.send_message(message.chat.id, 'Готов работать!', reply_markup=markup)


@mybot.message_handler(commands=['stop'])
def handle_stop(message):
    mybot.send_message(message.chat.id, 'Бот останавливается . . .')
    mybot.stop_bot()


@mybot.message_handler(content_types=['text'])
def view_get_trades(message):
    if message.chat.type == 'private':
        if message.text == 'Крипта':
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            brn1 = telebot.types.KeyboardButton('Узнать стоимость токена')
            brn2 = telebot.types.KeyboardButton('Вывести токены в диапозоне 12%')
            brn3 = telebot.types.KeyboardButton('Поиск просевших токенов')
            brn4 = telebot.types.KeyboardButton('Поиск выросших токенов')
            back = telebot.types.KeyboardButton('Назад')
            markup.add(brn1, brn2)
            markup.add(brn3, brn4)
            markup.add(back)
            mybot.send_message(message.chat.id, 'Выберите действие:', reply_markup=markup)
        elif message.text == 'Поиск просевших токенов':
            mybot.send_message(message.chat.id, 'Идет поиск . . .')
            token_down(message)
        elif message.text == 'Поиск выросших токенов':
            mybot.send_message(message.chat.id, 'Идет поиск . . .')
            token_up(message)
        elif message.text == 'Узнать стоимость токена':
            msg = mybot.send_message(message.chat.id, 'Укажите название токена:')
            mybot.register_next_step_handler(msg, after_text)
        elif message.text == 'Вывести токены в диапозоне 12%':
            mybot.send_message(message.chat.id, 'Идет поиск . . .')
            token_range(message)
        elif message.text == 'Курсы валют':
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            brn1 = telebot.types.KeyboardButton('Узнать курс $')
            brn2 = telebot.types.KeyboardButton('Узнать курс €')
            back = telebot.types.KeyboardButton('Назад')
            markup.add(brn1, brn2)
            markup.add(back)
            mybot.send_message(message.chat.id, 'Выберите валюту:', reply_markup=markup)
        elif message.text == 'Узнать курс $':
            data = requests.get(
                'https://free.currconv.com/api/v7/convert?apiKey=f03f1a2946ffc093e5f7&q=USD_RUB&compact=ultra').json()
            mybot.send_message(message.chat.id, f"{data['USD_RUB']:.2f}₽")
        elif message.text == 'Узнать курс €':
            data = requests.get(
            'https://free.currconv.com/api/v7/convert?apiKey=f03f1a2946ffc093e5f7&q=EUR_RUB&compact=ultra').json()
            mybot.send_message(message.chat.id, f"{data['EUR_RUB']:.2f}₽")
        elif message.text == 'Назад':
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            brn1 = telebot.types.KeyboardButton('Курсы валют')
            brn2 = telebot.types.KeyboardButton('Крипта')
            markup.add(brn1, brn2)
            mybot.send_message(message.chat.id, 'Вы в главном меню', reply_markup=markup)


def after_text(message):
    '''
    :param message: Поиск токена по имени, btc == BTCUSDT
    :return: Выводит стоимость токена, введеного в телеграм боте
    Не могу пока что реализовать, чтобы была помощь при вводе токена, искал из базы и подсказывал ввод,
    и чтобы после поиска не закрывалось меню телеграм бота.
    '''
    token_name = message.text.upper() + 'USDT'
    get_price_token()
    for key, value in token_info.items():
        if token_name == key:
            mybot.send_message(message.chat.id, value + '$')
            break
    else:
         mybot.send_message(message.chat.id, 'Скорее всего токен введен неверно, попробуй повторить поиск')


# timestamp = 1672012800000 / 1000  # переводим миллисекунды в секунды
# date = datetime.datetime.fromtimestamp(timestamp)
# print(date)


def token_range(message):
    get_price_token() # Получаем и записываем данные в словарь
    time.sleep(1)
    mybot.send_message(message.chat.id, 'Результат по запросу:')
    for key in token_info.keys():  # Перебираем все токены с параметрами, указанными ниже
        try:
            klines = [i[:5] for i in client.get_historical_klines(str(key), Client.KLINE_INTERVAL_1DAY,
                                                                   '7 day ago UTC')]  # За какой период подтягивать инфу, в данном случае это 7 дней
            kol_dnei = 0  # Кол-во дней по которым смотрим данные
            max_price_token = []  # Макс цена токена без учета деления на кол-во дней
            min_price_token = []  # Мин цена токена без учета деления на кол-во дней
            for price in klines:
                # open_date = datetime.datetime.fromtimestamp(int(klines[kol_dnei][0]) / 1000) # Дата открытия
                price_open = klines[kol_dnei][1]  # Цена открытя токена по ключу key из словаря token_info
                price_max = klines[kol_dnei][2]  # Цена максимума за сутки токена по ключу key из словаря token_info
                price_min = klines[kol_dnei][3]  # Цена минимума за сутки токена по ключу key из словаря token_info
                price_close = klines[kol_dnei][4]  # Цена закрытия токена по ключу key из словаря token_info
                # volume = klines[kol_dnei][5] # Объем торгов
                # close_date = datetime.datetime.fromtimestamp(int(klines[kol_dnei][6]) / 1000)  # Дата закрытия
                kol_dnei += 1
                max_price_token.append(price_max)
                min_price_token.append(price_min)
            price_deviation = myMath.change_price(max(*[float(i) for i in max_price_token]), min(*[float(i) for i in min_price_token]),
                                                  False)  # Отклонение цены в % за диапозон в n дней
            # print(f'{key} = {price_deviation}')
            if price_deviation < 12.0:
                mybot.send_message(message.chat.id, f'{key} торгуется в диапозоне: {price_deviation}%')
        except:
            pass
    mybot.send_message(message.chat.id, 'Список закончился!')


    # with pd.option_context("display.max_rows", None, "display.max_columns", None):
    #     print(f'***********{key}***********')
    #     informathion_about_token = pd.DataFrame(klines, columns=['Open time',
    #                                                         'Open',
    #                                                         'High',
    #                                                         'Low',
    #                                                         'Close',
    #                                                         'Volume'], dtype=float)
    #     print(informathion_about_token)
    #     print()
    #     with pd.ExcelWriter('informathion_about_token.xlsx', mode='a', engine='openpyxl') as writer:
    #         informathion_about_token.to_excel(writer, sheet_name=str(key), index=False)


def token_down(message): # Поиск монет упавших за два дня
    get_price_token() # Получаем и записываем данные в словарь
    time.sleep(1)
    mybot.send_message(message.chat.id, 'Результат по запросу:')
    for key in token_info.keys():  # Перебираем все токены с параметрами, указанными ниже
         try:
            klines = [i[2:4] for i in client.get_historical_klines(str(key), Client.KLINE_INTERVAL_1DAY,
                                                                   '2 day ago UTC')]  # За какой период подтягивать инфу, в данном случае это 2 дня
            kol_dnei = 0  # Кол-во дней по которым смотрим данные
            max_price_token = []  # Макс цена токена без учета деления на кол-во дней
            min_price_token = []  # Мин цена токена без учета деления на кол-во дней
            for price in klines:
                price_max = klines[kol_dnei][0]  # Цена максимума за сутки токена по ключу key из словаря token_info
                price_min = klines[kol_dnei][1]  # Цена минимума за сутки токена по ключу key из словаря token_info
                kol_dnei += 1
                max_price_token.append(price_max)
                min_price_token.append(price_min)
            price_deviation = myMath.down_price_token(max(*[float(i) for i in max_price_token]), min_price_token[1], False)
            if price_deviation > 15.0:
                mybot.send_message(message.chat.id, f'{key} = - {price_deviation}%')
         except:
             pass
    mybot.send_message(message.chat.id, 'Список закончился!')


def token_up(message): # Поиск монет выросших за два дня
    get_price_token() # Получаем и записываем данные в словарь
    time.sleep(1)
    mybot.send_message(message.chat.id, 'Результат по запросу:')
    for key in token_info.keys():  # Перебираем все токены с параметрами, указанными ниже
         try:
            klines = [i[2:4] for i in client.get_historical_klines(str(key), Client.KLINE_INTERVAL_1DAY,
                                                                   '2 day ago UTC')]  # За какой период подтягивать инфу, в данном случае это 2 дня
            kol_dnei = 0  # Кол-во дней по которым смотрим данные
            max_price_token = []  # Макс цена токена без учета деления на кол-во дней
            min_price_token = []  # Мин цена токена без учета деления на кол-во дней
            for price in klines:
                price_max = klines[kol_dnei][0]  # Цена максимума за сутки токена по ключу key из словаря token_info
                price_min = klines[kol_dnei][1]  # Цена минимума за сутки токена по ключу key из словаря token_info
                kol_dnei += 1
                max_price_token.append(price_max)
                min_price_token.append(price_min)
            price_deviation = myMath.change_price(max_price_token[1], min(*[float(i) for i in min_price_token]), False)
            if price_deviation > 15.0:
                mybot.send_message(message.chat.id, f'{key} = + {price_deviation}%')
         except:
             pass
    mybot.send_message(message.chat.id, 'Список закончился!')


mybot.polling()
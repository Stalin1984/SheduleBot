# coding = UTF-8

from bs4 import BeautifulSoup
import requests
import datetime
import pytz
from time import sleep
import sqlite3
import telebot
from TK import token


def cutFreeSpace(string):
    n = 0
    x = -1
    for y in string:
        x += 1
        if y == ' ':
            n += 1
            if n == 2:
                break
        else:
            n = 0
    return string[:x:]

def GetData():

    st = datetime.datetime.now()

    urls = ['https://www.asu.ru/timetable/students/24/2129440624/']

    print('Parsing is started')

    for url in urls:

        result = {}

        connection = sqlite3.connect('Data.db')
        cur = connection.cursor()

        rs = requests.get(url)

        soup = BeautifulSoup(rs.text, 'lxml')

        numberOfGroup = soup.h1.string.split()[2]

        TBODYschedule = soup.find('div', attrs={'class':'shedule_list margin_bottom_xx'}).find_all('tr')

        for x in TBODYschedule:

            if x.attrs['class'][0] == 'schedule-date':

                scData = x.find_all('span')
                infData = scData[0].text, scData[1].text
                result[infData] = []
            else:
                day = []
                scTime = x.contents
                try:
                    time = scTime[3].nobr.text
                except:
                    time = ''
                try:
                    a_or_b = x.find('span', attrs={'class':'t_gray'}).text.split()[0]
                except:
                    a_or_b = ''
                try:
                    form = scTime[5].contents[3].text
                except:
                    form = ''

                nameOfThing = cutFreeSpace(scTime[5].contents[4])

                try:
                    formatOfLearning = x.find('span', attrs={'class':'t_small'}).text
                except:
                    formatOfLearning = ''

                if len(formatOfLearning) == 0:
                    formatOfLearning = ''
                try:
                    teacher = x.find('span', attrs={'class':"t_gray_light_x t_small_x"}).text, \
                              x.find('a', attrs={'class': "light"}).text
                except:
                    teacher = '', ''
                try:
                    place = x.find('a', attrs={'class':'t_red'}).text
                except:
                    place = ''

                try:
                    place = place.replace('\xa0',' ')
                except:
                    pass

                day.append(infData[0])
                day.append(infData[1])
                day.append(numberOfGroup)
                day.append(time)
                day.append(a_or_b)
                day.append(form)
                day.append(nameOfThing)
                day.append(formatOfLearning)
                day.append(teacher[0])
                day.append(teacher[1])
                day.append(place)

                result[infData].append(day)

        scheduleData = {numberOfGroup: result}

        b = 0

        try:
            cur.execute('DROP TABLE imit')
        except:
            pass

        try:

            cur.execute(f" CREATE TABLE imit (time1 TEXT, time2 TEXT, nameOfGroup TEXT, name TEXT, subgroup TEXT, form TEXT, itemName TEXT, formatOfLearning TEXT, teacher1 TEXT, teacher2 TEXT, place TEXT)")
        except:
            print('already is exist')


        arr = []

        for x in result:
            #print(x)
            for y in result[x]:
                #print(y)
                arr.append(y)
        for y in arr:

            cur.execute("INSERT INTO imit VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", y)

        connection.commit()

        fn = datetime.datetime.now()

        print(fn - st)
        print('Parsing is completed')

def Bot():

    bot = telebot.AsyncTeleBot(token)
    while True:

        dict = {

            'Понедельник': [],
            'Вторник': [],
            'Среда': [],
            'Четверг': [],
            'Пятница': [],
            'Суббота': []

        }

        print('Bot get started!')

        try:

            @bot.message_handler(commands=['start', 'help'])
            def comands(message):
                if message.text == '/start':
                    firstName = message.from_user.first_name
                    lastName = message.from_user.last_name
                    bot.send_message(message.chat.id, f'Добро пожаловать в телеграм бота, {firstName} {lastName}')
                else:
                    bot.send_message(message.chat.id, 'Чтобы получить расписание напишите номер своей группы:'
                                                      'К примеру: 4.101-2')


            @bot.message_handler(func=lambda message: True)
            def getSch(message):

                if message.text == '4.101-2':
                    connection = sqlite3.connect('Data.db')
                    cur = connection.cursor()

                    for line in cur.execute('SELECT * FROM imit'):
                        dict[line[0]].append(line[1::])

                    text = ''
                    border = '////////////////////////////////////////////\n\n'
                    for x in dict:
                        text += f"{x} ({dict[x][0][0]})\n\n"
                        n = 1
                        t = 0
                        for y in dict[x]:
                            if y[3] == 'а)' or y[3] == 'б)':
                                t += 1
                                if t == 2:
                                    t = 0
                                    n -= 1
                            line = f'Пара №{n}\n Время: {y[2]}\n{y[3]} {y[4]}\n{y[5]}\n Формат: {y[6]}\n Преподаватель: {y[7]} {y[8]}\n Аудитория: {y[9]}\n\n'
                            text += line
                            n += 1
                        text += border

                    bot.send_message(message.chat.id, text)
                else:
                    bot.send_message(message.chat.id, 'К сожалению я еще не могу понять что это значит. '
                                                      'Возможно вы допустили ошибку в тексте, '
                                                      'либо данная функция еще не прописана')

            bot.polling()
        except Exception as ex:
            print(ex)
            sleep(1)


def Timer():
    while True:
        sleep(0.9)

        localZone = pytz.timezone('Asia/Novosibirsk')
        localTime = datetime.datetime.now(localZone)
        hour = localTime.strftime('%H:%M')

        print(hour)

        if hour == '01:00' or hour == '01:01':
            GetData()

GetData()
Bot()

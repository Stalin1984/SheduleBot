# coding = UTF-8

from bs4 import BeautifulSoup
import requests
import datetime
import pytz
import sqlite3
from aiogram import Bot, Dispatcher, types
import asyncio
from TK import token
from sys import exit


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

async def Timer():
    while True:
        await asyncio.sleep(0.9)

        localZone = pytz.timezone('Asia/Novosibirsk')
        localTime = datetime.datetime.now(localZone)
        hour = localTime.strftime('%H:%M:%S')

        if hour == '01:00:00' or hour == '01:00:01':
            print('Bot stoped')
            GetData()

BOT_TOKEN = token

async def start_handler(message: types.Message):
    await message.answer(
        f"Hello, {message.from_user.get_mention(as_html=True)} 👋!",
        parse_mode=types.ParseMode.HTML,
    )
async def echo(message: types.Message):

    days = {
        'Понедельник': [],
        'Вторник': [],
        'Среда': [],
        'Четверг': [],
        'Пятница': [],
        'Суббота': []
    }

    if message.text == '4.101-2':

        await message.answer('Подождите немного, пожалуйста')

        con = sqlite3.connect('Data.db')
        cur = con.cursor()
        for x in cur.execute('SELECT * FROM imit'):
            x = list(x)
            del x[2]
            days[x[0]].append(x[1::])

        text = 'Расписание: \n'
        border = '\n//////////////////////\n\n'

        for y in days:
            n = 0
            text += border

            text += f'{y} {days[y][0][0]}: \n\n'
            w = 0
            for z in days[y]:
                n += 1
                if z[2] == 'а)' or z[2] == 'б)':
                    w += 1
                    if w == 2:
                        w = 0
                        n -= 1
                if z[8] == '':
                    z[8] = '-----'
                if z[7] == '':
                    z[7] = '-----'
                text += f'Пара: № {str(n)} \n'
                text += f'Время:  {z[1]} \n{z[2]} {z[3]} {z[4]} {z[5]}\nПреподователь: {z[6]} {z[7]}\nАудитория: {z[8]} \n\n'

        await message.answer(text)
    else:
        await message.answer("Это не известная мне команда.")

async def main():
    bot = Bot(token=BOT_TOKEN)
    print('bot get started')
    while True:
        try:
            disp = Dispatcher(bot=bot)
            disp.register_message_handler(start_handler, commands={"start", "restart"})
            disp.register_message_handler(echo, lambda message: message.text)
            await disp.start_polling()
        except Exception as ex:
            print(ex)
            await asyncio.sleep(1)
        finally:
            await bot.close()

while True:
    st = input('Enter start to start. \nEnter exit to close program. \n>>>>>> ')

    if st == 'start':
        loop = asyncio.get_event_loop()
        tasks = [loop.create_task(main()), loop.create_task(Timer())]
        wait_tasks = asyncio.wait(tasks)
        loop.run_until_complete(wait_tasks)
    elif st == 'exit':
        exit()

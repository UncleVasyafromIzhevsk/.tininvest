import re
import datetime
import asyncio
import time

import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
import pandas as pd
import matplotlib.dates as mpl_dates
import numpy as np
from sklearn import preprocessing
from kivy.garden.matplotlib import FigureCanvasKivyAgg

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import (ScreenManager, Screen,
                                    FadeTransition, CardTransition)
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.uix.widget import Widget
from kivy.properties import (StringProperty, NumericProperty,
                             ListProperty, ObjectProperty, BooleanProperty,
                             BoundedNumericProperty, OptionProperty,
                             ReferenceListProperty,
                             AliasProperty, DictProperty,
                             VariableListProperty,
                             ConfigParserProperty,
                             ColorProperty
                             )

from tinkoff.invest import RequestError

from tinapi import Tin_API

# Получение токена из файла
token = None
with open('token.txt', 'r') as f:
    token = f.read()
print(token)
#Объект тинкофф
tin = Tin_API(token)
#Флаг перехода в основной апп
go_mainapp = False
#UID, FIGI and Name для временного хранения
gUID = ''
gFIGI = ''
gNAME = ''
#Флаги для заполнения экрана избранного
flag1 = False
flag2 = False
flag3 = False
flag4 = False
flag5 = False
closPrice1 = [0,0,0,0]
closPrice1 = [0,0,0,0]
closPrice1 = [0,0,0,0]
closPrice1 = [0,0,0,0]


# главный экран
class MainWindow(Screen):
    pass


# второй экран приложения
class ScreenInfoTools(Screen):
    pass

# Экран авторизации
class Authorization_Screen(Screen):
    pass


# Карты инструментов на экране портфеля
class CardTools(MDCard):
    name = ObjectProperty(None)
    uid = StringProperty()
    figi = StringProperty()
    ticker = StringProperty()
    class_code = StringProperty()
    isin = StringProperty()
    lot = NumericProperty()
    currency = StringProperty()
    name_sh = StringProperty()
    exchange = StringProperty()
    country_of_risk_name = StringProperty()
    sector = StringProperty()
    buy_available_flag = BooleanProperty()
    sell_available_flag = BooleanProperty()
    api_trade_available_flag = BooleanProperty()
    for_qual_investor_flag = BooleanProperty()
    real_exchange = StringProperty()
    lot_str = StringProperty()
    price = StringProperty()
    percent = StringProperty()
    percent_color = ColorProperty()
    price_lot = StringProperty()
    def __init__(self, *arg):
        # Родительский конструктор
        MDCard.__init__(self)
        # Свой конструктор
        self.uid = arg[0]
        self.figi = arg[1]
        self.ticker = arg[2]
        self.class_code = arg[3]
        self.isin = arg[4]
        self.lot = arg[5]
        self.currency = arg[6]
        self.name_sh = arg[7]
        self.exchange = arg[8]
        self.country_of_risk_name = arg[9]
        self.sector = arg[10]
        self.buy_available_flag = arg[11]
        self.sell_available_flag = arg[12]
        self.api_trade_available_flag = arg[13]
        self.for_qual_investor_flag = arg[14]
        self.real_exchange = arg[15]
        self.lot_str = str(self.lot)
        self.price = ''
        self.percent = ''
        self.percent_color = 'black'
        self.percent_lot = ''

# Линия графика
class GridGraph(Widget):
    name = ObjectProperty(None)
    x1 = NumericProperty()
    x2 = NumericProperty()
    y1 = NumericProperty()
    y2 = NumericProperty()
    def __init__(self, *arg):
        # Родительский конструктор
        Widget.__init__(self)
        # Свой конструктор
        self.x1 = arg[0]
        self.y1 = arg[1]
        self.x2 = arg[2]
        self.y2 = arg[3]


# Свеча графика
class CandleGraph(Widget):
    name = ObjectProperty(None)
    x1 = NumericProperty()
    x2 = NumericProperty()
    x3 = NumericProperty()
    x4 = NumericProperty()
    y1 = NumericProperty()
    y2 = NumericProperty()
    y3 = NumericProperty()
    y4 = NumericProperty()
    def __init__(self, *arg):
        # Родительский конструктор
        Widget.__init__(self)
        # Свой конструктор
        self.x1 = arg[0]
        self.y1 = arg[1]
        self.x2 = arg[2]
        self.y2 = arg[3]
        self.x3 = arg[4]
        self.y3 = arg[5]
        self.x4 = arg[6]
        self.y4 = arg[7]


class TinvestApp(MDApp):
    #Объявление объулта карты инструмента
    card_Tools = {}
    card_Tools_Portf = {}
    # Определение асинх задач
    # Задача для получения, записи и отображения всех акций
    get_all_shares_task = None
    # Задача для получения, записи цен всех акций
    get_all_prices_share_task = None
    # other_task3 = None
    def build(self):
        sm = ScreenManager(transition=CardTransition())
        sm.add_widget(Authorization_Screen(name='login'))
        sm.add_widget(MainWindow(name='main'))
        sm.add_widget(ScreenInfoTools(name='screen_info_tools'))
        return sm

    #Определение screen и работа с id kv
    def screen_def(self):
        # Определяем ссылку на screen
        name_scr = (re.split("'|'", (str(self.root.children)))[1])
        # Определяем объек screen
        a = self.root.get_screen(name_scr).ids
        return a

    #Очистка текстового виджита
    def clean_text_widg(self, r):
        a = self.screen_def()
        a.r.hint_text = 'ujjj'
    #Включение флага перехода на основной апп
    def go_main(self):
        global go_mainapp
        go_mainapp = True
        print(go_mainapp)

    # Функция для асинх задач
    def walking_nearby(self):
        # Задачам передаем фукции
        # Получение, запись и отображение всех акций
        self.get_all_shares_task = asyncio.ensure_future(
            self.get_all_shares())
        # Получение, запись цен всех акций
        self.get_all_prices_share_task = asyncio.ensure_future(
            self.async_price())
        # self.other_task3 = asyncio.ensure_future(self.async_func2())
        async def run_wrapper():
            await self.async_run(async_lib='asyncio')
            print('App done')
            self.get_all_shares_task()
            self.get_all_prices_share_task.cancel()
            #self.other_task3.cancel()
        return asyncio.gather(run_wrapper(), self.get_all_shares_task,
                              self.get_all_prices_share_task)
        # self.other_task3)#

    # Асинхроные корутины
    # Корутина по всем акциям
    async def get_all_shares(self):
        global go_mainapp
        print(go_mainapp)
        #Ждем пока не сработал флаг перехода на основной экран
        while not go_mainapp:
            await asyncio.sleep(2)
            print(go_mainapp)
        #Перешли на основной экран
        a_id = self.screen_def()
        print(a_id.shares_box)
        b = await tin.tin_req_all_shares()
        #print(b)
        i = 1
        for a in b.instruments[:-1]:
            print(a.name)
            if (
                    a.api_trade_available_flag == 1
                    and a.for_qual_investor_flag == 0
                    and a.buy_available_flag == 1
                    and a.sell_available_flag == 1
                    and a.currency == 'rub'):
                get_price = await tin.tin_req_prices_share(figi={a.figi},
                                                           instrument_id={
                                                               a.uid})
                get_percent = await tin.tin_req_percent(a.figi, a.uid)
                try:
                    print(get_percent[0])
                    print(get_percent[1])
                except TypeError:
                    print(' - ', 'black')
                get_price_lot = await tin.tin_req_prices_lot(figi={a.figi},
                                                             instrument_id={
                                                               a.uid})
                self.card_Tools[i] = CardTools(a.uid, a.figi, a.ticker,
                                               a.class_code, a.isin, a.lot,
                                               a.currency,
                                               a.name, a.exchange,
                                               a.country_of_risk_name,
                                               a.sector,
                                               a.buy_available_flag,
                                               a.sell_available_flag,
                                               a.api_trade_available_flag,
                                               a.for_qual_investor_flag,
                                               a.real_exchange.name)
                self.card_Tools[i].price = get_price
                try:
                    self.card_Tools[i].percent = get_percent[0]
                    self.card_Tools[i].percent_color = get_percent[1]
                except TypeError:
                    self.card_Tools[i].percent = ' - '
                    self.card_Tools[i].percent_color = 'black'
                price_lot1 = get_price_lot * int(a.lot)
                price_lot2 = round(price_lot1, 2)
                self.card_Tools[i].price_lot = ('Цена за лот: ' +
                                                   str(price_lot2) + ' руб')
                print(self.card_Tools[i].price_lot)
                a_id.shares_box.add_widget(self.card_Tools[i])
                print('экземпляр ' + str(id(self.card_Tools[i])))
                i += 1
        keysList = list(self.card_Tools.keys())
        print((keysList))

    # Корутина по ценам акций
    async def async_price(self):
        global go_mainapp
        print(go_mainapp)
        # Ждем пока не сработал флаг перехода на основной экран
        while not go_mainapp:
            await asyncio.sleep(2)
            print(go_mainapp)
        # Пауза для того чтоб не ушел в цикл до получения
        # первых акций
        await asyncio.sleep(20)
        while True:
            # Пауза между циклами отпрса
            await asyncio.sleep(20)
            print('ap')
            if (list(self.card_Tools.keys())) != []:
                i = 1
                b = list(self.card_Tools.keys())[-1]
                for a in range(1, b):
                    x = self.card_Tools[i]
                    print(x.name_sh)
                    get_price_lot = await tin.tin_req_prices_lot(figi={x.figi},
                                                                 instrument_id={
                                                                     x.uid})
                    a = await tin.tin_req_prices_share(figi={x.figi},
                                                       instrument_id={
                                                           x.uid})
                    с = await tin.tin_req_percent(x.figi, x.uid)
                    self.card_Tools[i].price = a
                    price_lot1 = get_price_lot * int(x.lot)
                    price_lot2 = round(price_lot1, 2)
                    self.card_Tools[i].price_lot = ('Цена за лот: ' +
                                                    str(price_lot2) + ' руб')
                    print(self.card_Tools[i].price_lot)
                    try:
                        self.card_Tools[i].percent = с[0]
                        self.card_Tools[i].percent_color = с[1]
                    except TypeError:
                        self.card_Tools[i].percent = ' - '
                        self.card_Tools[i].percent_color = 'black'
                    i += 1
                    t = time.localtime()
                    current_time = time.strftime(
                        "Текущее время - %H:%M:%S", t)
                    print(current_time)
                    # Паузы между запросами по акциям
                    await asyncio.sleep(5)
            else:
                print('fin')
                break

    # Авторизация на начальной странице
    def token_auth(self):
        print(token)
        tininfo = tin.tin_tariff()
        tinschet = tin.tin_schet()
        tinavail = tin.tin_portf(tinschet.accounts[0].id)
        a = self.screen_def()
        print(a.tinuserinfo)
        #Применяем команды к виджетам по id
        a.tinuserinfo.text = """
        Наименование тарифа пользователя: {}\n
        Идентификатор счёта: {}\n
        Общая стоимость портфеля: {},{} Рублей\n
        Текущая относительная доходность портфеля: {},{} %\n
        Общая стоимость валют в портфеле: {},{} Рублей\n
        Общая стоимость акций в портфеле: {},{} Рублей 
        """.format(tininfo.tariff, tinschet.accounts[0].id,
                   str(tinavail.total_amount_portfolio.units),
                   (str(tinavail.total_amount_portfolio.nano).split()[0][0:2]),
                   str(tinavail.expected_yield.units),
                   str(tinavail.expected_yield.nano),
                   str(tinavail.total_amount_currencies.units),
                   (str(tinavail.total_amount_currencies.nano).split()[0][0:2]),
                   str(tinavail.total_amount_shares.units),
                   (str(tinavail.total_amount_shares.nano)).split()[0][0:2])

    # Функция при запуске приложения
    def on_start(self):
        global token
        global go_mainapp
        a = self.screen_def()
        print(a)
        if token == '':
            a.tinuserinfo.text = 'Введите токен'
        if token != '':
            try:
                self.token_auth()
                a.go_next.disabled = False
            except RequestError:
                a.tinuserinfo.text = 'Токен доступа не найден или не активен'

    #Ввод токена
    def token_input(self, *args):
        global go_mainapp
        a = self.screen_def()
        with open('token.txt', 'w') as f:
            f.write(args[0])
        tin.token = args[0]
        try:
            self.token_auth()
            a.go_next.disabled = False
        except RequestError:
            a.tinuserinfo.text = 'Токен доступа не найден или не активен'
            a.go_next.disabled = True

    #Страница портфеля
    #Обновление данных портфеля
    def portfolio_data(self):
        tinschet = tin.tin_schet()
        tinavail = tin.tin_portf(tinschet.accounts[0].id)
        a_id = self.screen_def()
        a_id.tot_portf_val.text = """
        {},{} Рублей
        """.format(str(tinavail.total_amount_portfolio.units),
                   (str(tinavail.total_amount_portfolio.nano).split()[0][0:2]))
        a_id.tot_val_curr_portf.text = """
        {},{} Рублей
        """.format(str(tinavail.total_amount_currencies.units),
                   (str(tinavail.total_amount_currencies.nano).split()[0][0:2]))
        myShare = tin.tin_getting_positions(tinschet.accounts[0].id)
        print(myShare[0])
        print(myShare[1][1].instrument_uid)
        i = 0
        if myShare[0] != 0:
            print(myShare[1][::-1])
            for c in myShare[1][::-1]:
                print(c)
                b = tin.tin_my_shares(c.instrument_uid)
                print(c)
                print(b)
                print(myShare[1][i])
                a = b.instrument
                print(a)
                d = myShare[1][i].balance
                print(d)

                print(a.name)

                self.card_Tools_Portf[i] = CardTools(a.uid, a.figi,
                                                     a.ticker, a.class_code,
                                                     a.isin, a.lot, a.currency,
                                                     a.name, a.exchange,
                                                     a.country_of_risk_name,
                                                     a.sector,
                                                     a.buy_available_flag,
                                                     a.sell_available_flag,
                                                     a.api_trade_available_flag,
                                                     a.for_qual_investor_flag,
                                                     a.real_exchange.name
                                                     )
                get_price = tin.tin_req_prices_shar(figi={a.figi},
                                                    instrument_id={a.uid}
                                                    )
                self.card_Tools_Portf[i].price = (str(get_price) + ' Рублей')
                price_lot1 = get_price * int(d)
                price_lot2 = round(price_lot1, 2)
                self.card_Tools_Portf[i].price_lot = ('Всего лотов ' + str(d) +
                                                ' На сумму: ' +
                                                str(price_lot2) + ' руб')
                #print(self.card_Tools[i].price_lot)
                a_id.inNali_box.add_widget(self.card_Tools_Portf[i])
                print('экземпляр ' + str(id(self.card_Tools_Portf[i])))
                i += 1



    #Страница информации по акции
    # Очистка экрана
    # графика экрана инструмента
    def clear_graf(self):
        name_scr = re.split("'|'", (str(self.root.children)))[1]
        self.root.get_screen(name_scr).ids.plot.clear_widgets(
            children=None)

    # Линейный график
    # Переменки для заполнения экрана избранного
    flag1 = False
    flag2 = False
    flag3 = False
    flag4 = False
    flag5 = False
    closPrice1 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    closPrice2 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    closPrice3 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    closPrice4 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    closPrice5 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    #Сам график
    def line_graph(self):
        global gUID
        global gFIGI
        global gNAME
        a_id = self.screen_def()
        a_id.plot_line.clear_widgets(
            children=None)
        lst = (tin.tin_plot_line(gFIGI, gUID))
        candTime = lst[0]
        closPrice = lst[4]
        if not self.flag1:
            self.flag1 = True
            if self.flag1:
                self.closPrice1 = closPrice
                a_id.promoShare1.text = gNAME
        elif not self.flag2:
            self.flag2 = True
            if self.flag2:
                self.closPrice2 = closPrice
                a_id.promoShare2.text = gNAME
        elif not self.flag3:
            self.flag3 = True
            if self.flag3:
                self.closPrice3 = closPrice
                a_id.promoShare3.text = gNAME
        elif not self.flag4:
            self.flag4 = True
            if self.flag4:
                self.closPrice4 = closPrice
                a_id.promoShare4.text = gNAME
        elif not self.flag5:
            self.flag5 = True
            if self.flag5:
                self.closPrice5 = closPrice
                a_id.promoShare5.text = gNAME
        else: print('Места в избранном закончены')
        fig, ax = plt.subplots()
        # Прозрачность фигуры
        fig.patch.set_alpha(0)
        #Сам график
        share_bign = np.array([self.closPrice1, self.closPrice2,
                               self.closPrice3, self.closPrice4,
                               self.closPrice5
                               ]
                              )
        share_plot = preprocessing.normalize(share_bign)
        #print(share_plot)
        ax.plot(candTime, share_plot[0], color='r', marker='o')
        ax.plot(candTime, share_plot[1], color='b', marker='o')
        ax.plot(candTime, share_plot[2], color='y', marker='o')
        ax.plot(candTime, share_plot[3], color='g', marker='o')
        ax.plot(candTime, share_plot[4], color='tab:brown', marker='o')
        # Прозрачность фона графика
        ax.patch.set_alpha(0)
        #Удаление значений оси y
        ax.get_yaxis().set_visible(False)
        # аннотации:
        #ax.set_xticklabels(share_bign)

        # Сетка графика
        #plt.grid(color='k', linestyle='-', linewidth=0.1)
        #Сборка графика
        canvas = FigureCanvasKivyAgg(fig)
        #добавление графика в виджет
        a_id.plot_line.add_widget(canvas)
    #Удаление акции из избранного
    def removing_share_favorites(self, *args):
        a_id = self.screen_def()
        if args[0] == 'favorites1':
            self.flag1 = False
            self.closPrice1 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            a_id.promoShare1.text = 'Удален из избранного'
        if args[0] == 'favorites2':
            self.flag2 = False
            self.closPrice2 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            a_id.promoShare2.text = 'Удален из избранного'
        if args[0] == 'favorites3':
            self.flag3 = False
            self.closPrice3 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            a_id.promoShare3.text = 'Удален из избранного'
        if args[0] == 'favorites4':
            self.flag4 = False
            self.closPrice4 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            a_id.promoShare4.text = 'Удален из избранного'
        if args[0] == 'favorites5':
            self.flag5 = False
            self.closPrice5 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            a_id.promoShare5.text = 'Удален из избранного'


    # График японских свеч
    def japan_candle(self, *args):
        global gUID
        global gFIGI
        global gNAME
        gUID = args[1]
        gFIGI = args[2]
        gNAME = args[0]
        a_id = self.screen_def()
        a_id.jap_cand_plot.clear_widgets(
            children=None)
        a_id.share_name.text = args[0]
        #print(tin.tin_plot_candle(args[2], args[1]))
        lst = (tin.tin_plot_candle(args[2], args[1]))
        candTime = lst[0]
        openPrice = lst[1]
        maxPrice = lst[2]
        minPrice = lst[3]
        closPrice = lst[4]
        stock_prices = pd.DataFrame({'date': candTime,
                                     'open': openPrice,
                                     'close': closPrice,
                                     'high': maxPrice,
                                     'low': minPrice
                                     }
                                    )

        ohlc = stock_prices.loc[:, ['date', 'open', 'high', 'low', 'close']]
        ohlc['date'] = pd.to_datetime(ohlc['date'])
        ohlc['date'] = ohlc['date'].apply(mpl_dates.date2num)
        ohlc = ohlc.astype(float)

        fig, ax = plt.subplots()
        fig.patch.set_alpha(0)
        # Сетка графика
        plt.grid(color='k', linestyle='-', linewidth=0.1)
        #Сам график свечей
        candlestick_ohlc(ax, ohlc.values, width=0.008, colorup='green',
                         colordown='red', alpha=1)

        ax.set_xlabel('Время')
        ax.set_ylabel('Цена, рубль')
        fig.suptitle('Динамика')

        date_format = mpl_dates.DateFormatter('%d %H:%M')
        ax.xaxis.set_major_formatter(date_format)
        ax.patch.set_alpha(0)
        fig.autofmt_xdate()

        canvas = FigureCanvasKivyAgg(fig)
        a_id.jap_cand_plot.add_widget(canvas)

#Запуск приложения с асинхронными коруттинами
loop = asyncio.get_event_loop()
loop.run_until_complete(TinvestApp().walking_nearby())
loop.close()


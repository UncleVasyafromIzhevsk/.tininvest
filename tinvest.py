import re
import datetime
import asyncio
import time

import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
import pandas as pd
import matplotlib.dates as mpl_dates
import numpy as np
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
#переменная для информации по брендам
brandInfo = ''

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
                print('Цена лота: ' + self.card_Tools[i].price_lot)
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
                    a = await tin.tin_req_prices_share(figi={x.figi},
                                                       instrument_id={
                                                           x.uid})
                    с = await tin.tin_req_percent(x.figi, x.uid)
                    self.card_Tools[i].price = a
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
                   str(tinavail.total_amount_portfolio.nano),
                   str(tinavail.expected_yield.units),
                   str(tinavail.expected_yield.nano),
                   str(tinavail.total_amount_currencies.units),
                   str(tinavail.total_amount_currencies.nano),
                   str(tinavail.total_amount_shares.units),
                   str(tinavail.total_amount_shares.nano))

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
                self.brand_info()
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
            self.brand_info()
        except RequestError:
            a.tinuserinfo.text = 'Токен доступа не найден или не активен'
            a.go_next.disabled = True

    #Страница портфеля
    #Обновление данных портфеля
    def portfolio_data(self):
        tinschet = tin.tin_schet()
        tinavail = tin.tin_portf(tinschet.accounts[0].id)
        a = self.screen_def()
        a.tot_portf_val.text = """
        {},{} Рублей
        """.format(str(tinavail.total_amount_portfolio.units),
                   str(tinavail.total_amount_portfolio.nano))
        a.tot_val_curr_portf.text = """
        {},{} Рублей
        """.format(str(tinavail.total_amount_currencies.units),
                   str(tinavail.total_amount_currencies.nano))

    #Страница информации по акции
    #Запрос информации по брендам
    def brand_info(self):
        global brandInfo
        brandInfo = tin.tin_brandsinfo()
    #Заполнение оена информации акции
    def full_descr_share(self, *args):
        global brandInfo
        a_id = self.screen_def()
        #print(a_id.share_name)
        a_id.share_name.text = ''
        a_id.share_sector.text = ''
        a_id.share_description.text = ''
        a_id.share_name.text = args[0]
        a_id.share_sector.text = 'Информация: \n{}'.format(
            brandInfo.brands[0].info
        )
        a_id.share_description.text = 'Описание: \n{}\n{}'.format(
            brandInfo.brands[0].description,
            brandInfo.brands[0].name
        )
        #a_id.share_description.text =
        #print('ОПИСАНИЕ: ', tin.tin_brandinfo(args[2]))
        # self.content_Info_Tools[0] = Content_Info_Tools(args[0])
        # a_id.screen_IT.add_widget(self.content_Info_Tools[0])

    # Сетка графика эк. инструмента
    def graf_line(self):
        name_scr = re.split("'|'", (str(self.root.children)))[1]
        plot = self.root.get_screen(name_scr).ids.plot
        a = (plot.size[0] / 9)
        b = (plot.size[1] / 9)
        c = 1
        while c < 9:
            c += 1
            plot.add_widget(GridGraph(a, plot.pos[1], a, plot.size[1])
                            )
            plot.add_widget(GridGraph(plot.pos[0], b, plot.size[0], b)
                            )
            a = ((plot.size[0] / 9) * c)
            b = ((plot.size[1] / 9) * c)

    # Очистка экрана
    # графика экрана инструмента
    def clear_graf(self):
        name_scr = re.split("'|'", (str(self.root.children)))[1]
        self.root.get_screen(name_scr).ids.plot.clear_widgets(
            children=None)

    # Линейный график
    def line_graph(self):
        name_scr = re.split("'|'", (str(self.root.children)))[1]
        plot = self.root.get_screen(name_scr).ids.plot
        fig, ax = plt.subplots()
        # Прозрачность фигуры
        fig.patch.set_alpha(0)
        ax.plot([1, 2, 3, 4])
        # Прозрачность фона графика
        ax.patch.set_alpha(0)
        canvas = FigureCanvasKivyAgg(fig)
        plot.add_widget(canvas)

    # График японских свеч
    def japan_candle(self):
        name_scr = re.split("'|'", (str(self.root.children)))[1]
        plot = self.root.get_screen(name_scr).ids.plot
        stock_prices = pd.DataFrame(
            {'date': np.array([datetime.datetime(
                2021, 11, i + 1)
                for i in range(14)]),
                'open': [36, 56, 45, 29, 65, 66, 67, 36, 56, 45, 29, 65, 66, 67],
                'close': [29, 72, 11, 4, 23, 68, 45, 29, 72, 11, 4, 23, 68, 45],
                'high': [42, 73, 61, 62, 73, 56, 55, 42, 73, 61, 62, 73, 56, 55],
                'low': [22, 11, 10, 2, 13, 24, 25, 22, 11, 10, 2, 13, 24, 25]
            }
        )

        ohlc = stock_prices.loc[:, ['date', 'open', 'high', 'low', 'close']]
        ohlc['date'] = pd.to_datetime(ohlc['date'])
        ohlc['date'] = ohlc['date'].apply(mpl_dates.date2num)
        ohlc = ohlc.astype(float)

        fig, ax = plt.subplots()
        fig.patch.set_alpha(0)
        # Сетка графика
        plt.grid(color='b', linestyle='-', linewidth=0.3)

        candlestick_ohlc(ax, ohlc.values, width=0.4, colorup='green',
                         colordown='red', alpha=1)

        ax.set_xlabel('Дата')
        ax.set_ylabel('Цена')
        fig.suptitle('Динамика')

        date_format = mpl_dates.DateFormatter('%d-%m-%Y')
        ax.xaxis.set_major_formatter(date_format)
        ax.patch.set_alpha(0)
        fig.autofmt_xdate()

        canvas = FigureCanvasKivyAgg(fig)
        plot.add_widget(canvas)

#Запуск приложения с асинхронными коруттинами
loop = asyncio.get_event_loop()
loop.run_until_complete(TinvestApp().walking_nearby())
loop.close()


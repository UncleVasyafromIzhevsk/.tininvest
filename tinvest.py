import re
import datetime

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
#Объект тинкофф
tin = Tin_API(token)

# главный экран
class MainWindow(Screen):
    pass


# второй экран приложения
class Screen_Info_Tools(Screen):
    pass


# Экран авторизации
class Authorization_Screen(Screen):
    pass


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
    def build(self):
        sm = ScreenManager(transition=CardTransition())
        sm.add_widget(Authorization_Screen(name='login'))
        sm.add_widget(MainWindow(name='main'))
        sm.add_widget(Screen_Info_Tools(name='screen_info_tools'))
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
        a = self.screen_def()
        a.tot_portf_val.text = """
        {},{} Рублей
        """.format(str(tinavail.total_amount_portfolio.units),
                   str(tinavail.total_amount_portfolio.nano))
        a.tot_val_curr_portf.text = """
        {},{} Рублей
        """.format(str(tinavail.total_amount_currencies.units),
                   str(tinavail.total_amount_currencies.nano))

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


TinvestApp().run()

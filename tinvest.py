import re
import numpy as np

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import (
    ScreenManager, Screen,
    FadeTransition, CardTransition)
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.uix.widget import Widget
from kivy.graphics import *
from kivy.properties import (
    StringProperty, NumericProperty,
    ListProperty, ObjectProperty,
    BooleanProperty,
    BoundedNumericProperty,
    OptionProperty,
    ReferenceListProperty,
    AliasProperty, DictProperty,
    VariableListProperty,
    ConfigParserProperty,
    ColorProperty
)


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
        sm = ScreenManager(
            transition=
            CardTransition()
        )
        sm.add_widget(
            Authorization_Screen(
                name='login')
        )
        sm.add_widget(MainWindow(
            name='main')
        )
        sm.add_widget(
            Screen_Info_Tools(
                name=
                'screen_info_tools')
        )
        return sm

    # Сетка графика эк. инструмента
    def graf_line(self):
        # print(type(
        # self.root.children)
        # )
        name_scr = re.split(
            "'|'", (str(
                self.root.children)
            )
        )[1]
        # print(re.split("'|'", (
        # str(self.root.children)
        # ))[1])
        # print(
        # self.root.get_screen(
        # re.split("'|'", (str(
        # self.root.children))
        # )[1]).ids)
        plot = self.root.get_screen(
            name_scr).ids.plot
        # print(plot.pos)
        # print(plot.size)
        a = (plot.size[0] / 9)
        b = (plot.size[1] / 9)
        c = 1
        while c < 9:
            c += 1
            plot.add_widget(
                GridGraph(
                    a,
                    plot.pos[1], a,
                    plot.size[1])
            )
            plot.add_widget(
                GridGraph(
                    plot.pos[0],
                    b, plot.size[0],
                    b)
            )
            a = (
                    (plot.size[0] / 9
                     ) * c
            )
            b = (
                    (plot.size[1] / 9
                     ) * c
            )

    # Очистка экрана
    # графика экрана инструмента
    def clear_graf(self):
        name_scr = re.split(
            "'|'", (str(
                self.root.children)
            )
        )[1]
        self.root.get_screen(
            name_scr).ids.plot.clear_widgets(
            children=None)

    # Свеча графика
    def graf_candle(self):
        name_scr = re.split(
            "'|'", (str(
                self.root.children)
            )
        )[1]
        plot = self.root.get_screen(
            name_scr
        ).ids.plot

        data = np.array(
            [[0, plot.size[1]],
             [69, 67], [120, 110]]
        )
        scaled_data = (data -
                       np.mean(data,
                               axis=0
                               )
                       ) / np.std(
            data, axis=0
        )
        print(scaled_data)

        # print(y1, y2)
        # plot.add_widget(
        # CandleGraph((
        # plot.size[0] / 9), y1,
        # (plot.size[0] / 9),
        # y2, 65, 43, 65, 45))


TinvestApp().run()

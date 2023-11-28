from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card import MDCard
from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout

from url_request.url_request import UrlRequest

import os
import sys

# Обработка ошибок
from tinkoff.invest import RequestError

# Получение токена из файла
token = None
with open('token.txt', 'r') as f:
            token = f.read()
            
# Объект для работы с запросами
url = UrlRequest(token)
    
# id счета(пока одного)
def id_score():
    try:
        a = str((url.url_req_schet()).accounts[0].id)
        return a
    except RequestError:
        a = None
        return a
idScore = id_score()

   
# Диалог ввода токена
class EnterToken(MDBoxLayout):
    adaptive_height=True
        
        
# Карты инструментов на экране портфеля
class CardTools(MDCard):
    text = StringProperty()
    

class Tinvest(MDApp):
    
    # Настройки портфеля
    enter_token = None
    
    def build(self):
        #self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = 'Green'

        return Builder.load_file ('./kv/tinvest.kv')
    
    
    
    # Запись токена
    def token_entry(self, tokken):
        _token = tokken
        with open('token.txt', 'w') as f:
            f.write(_token)
        url.token = _token
        
       
       
    # Настройки портфеля
    def show_confirmation_dialog (self):        
        if not self.enter_token:
            self.enter_token = MDDialog (                
                type="custom",
                md_bg_color='#2F4F4F',
                content_cls=EnterToken(),                
            )
        self.enter_token.open ()


    # Функция при запуске приложения
    def on_start(self):
        try:
            if token != '':
                print(url.token)
                getattr(self.root.ids, 'name_tariff').text = str(url.url_req_tariff().tariff)
                getattr(self.root.ids, 'value_portfolio').text = (str((
                    url.url_req_portf(idScore).total_amount_shares).units) + ',' + str((
                    url.url_req_portf(idScore).total_amount_shares).nano) +
                                                              ' ' + 'Рублей')
            else:
                getattr(self.root.ids, 'name_tariff').text = ('Не указан токен')
                getattr(self.root.ids, 'value_portfolio').text = ('Не указан токен')      
        except RequestError:
            getattr(self.root.ids, 'name_tariff').text = ('Токен не верен или просрочен')
            getattr(self.root.ids, 'value_portfolio').text = ('Токен не верен или просрочен')
        
        for brand in range(1, 20):
            self.root.ids.inNali_box.add_widget(
                CardTools(                                        
                    text=str(brand),                    
                )
            )
            
    
    

Tinvest().run()
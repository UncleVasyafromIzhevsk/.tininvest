from tinkoff.invest.sandbox.client import SandboxClient
from tinkoff.invest.constants import INVEST_GRPC_API_SANDBOX
# Для работы с методами клиента
from tinkoff.invest import (Client, MoneyValue, OrderDirection,
                            OrderType, PostOrderResponse, Operation,
                            InstrumentIdType)
from tinkoff.invest import CandleInterval

import uuid





# Получение токена из файла
token = None
with open('token.txt', 'r') as f:
    token = f.read()

#Идентификатор счета
def tin_check():
    with SandboxClient(token) as client:
        a = (client.users.get_accounts())
        print(a)

#Запрс денежек
def tin_many_in():
    with SandboxClient(token) as client:
        a = (client.sandbox.sandbox_pay_in(
            account_id='92e73909-a64c-4796-bde6-af3053c65f3b',
            amount=MoneyValue(currency='rub', units=10000, nano=0)
        ))
        print(a)

#Запрос выставления торгового поручения(покупка)
def post_sandbox_order():
    order_id = uuid.uuid4().hex
    order_id1 = order_id.split()[0][0:7]
    order_id2 = order_id.split()[0][7:11]
    order_id3 = order_id.split()[0][11:15]
    order_id4 = order_id.split()[0][15:19]
    order_id5 = order_id.split()[0][19:-1]
    order_id_ready = (order_id1 + '-' + order_id2 + '-' + order_id3 + '-' +
                      order_id4 + '-' + order_id5)
    print(order_id_ready)
    with SandboxClient(token) as client:
        a = client.orders.post_order(quantity=2,
                                     direction=OrderDirection.ORDER_DIRECTION_BUY,
                                     account_id='92e73909-a64c-4796-bde6-af3053c65f3b',
                                     order_type=OrderType.ORDER_TYPE_MARKET,
                                     #order_id - видемо рондомное число
                                     order_id=order_id_ready,
                                     instrument_id='BBG000GQSVC2',
        )
        print(a)

#Получение акций
def receiving_shares():
    with SandboxClient(token) as client:
        a = (client.instruments.shares())
        for i in a.instruments[:-1]:
            if i.currency == 'rub':
                print('Название: ',i.name,'\n','FIGI: ',i.figi,'\n',
                      'Идентификатор инструмента: ',i.uid,'\n',
                      'Lot: ', i.lot,'\n','Цена: ', i.nominal)
                z = ('Name: {}\nFIGI: {}\nID: {}\n'
                     'Lot: {}\nPrice: {}\n').format(i.name,i.figi,i.uid,i.lot,
                                                    i.nominal)
                with open('share.txt', 'a') as f:
                    f.write(z)

#Запрос информации по пользователю
def user_info():
    with SandboxClient(token) as client:
        a = (client.users.get_info())
        print(a)

#Списка операций по счёту
def list_transactions():
    with SandboxClient(token) as client:
        a = (client.operations.get_operations(
            account_id='92e73909-a64c-4796-bde6-af3053c65f3b'))
        print(a)

#Метод получения списка позиций по счёту
def getting_positions():
    with SandboxClient(token) as client:
        a = (client.operations.get_positions(
            account_id='92e73909-a64c-4796-bde6-af3053c65f3b'))
        print(a.money)  # денег
        print(a.securities)  # массив акций
        print(a.securities[1].figi)  # figi
        print(a.securities[1].instrument_uid)  # instrument_uid
        print(a.securities[1].balance)  # balance (сколько лотов)
        print(len(a.securities))  # количество позиций

#Запрос доступного для вывода остатка
def available_balance_withdrawal():
    with SandboxClient(token) as client:
        a = (client.operations.get_withdraw_limits(
            account_id='92e73909-a64c-4796-bde6-af3053c65f3b'))
        print(a.money)

#Запрос выставления торгового поручения(покупка)
def post_sandbox_order_sale():
    order_id = uuid.uuid4().hex
    order_id1 = order_id.split()[0][0:7]
    order_id2 = order_id.split()[0][7:11]
    order_id3 =order_id.split()[0][11:15]
    order_id4 = order_id.split()[0][15:19]
    order_id5 = order_id.split()[0][19:-1]
    order_id_ready = (order_id1 + '-' + order_id2 + '-' + order_id3 + '-' +
                      order_id4 + '-' + order_id5)
    print(order_id_ready)
    with SandboxClient(token) as client:
        a = client.orders.post_order(quantity=1,
                                     direction=OrderDirection.ORDER_DIRECTION_SELL,
                                     account_id='92e73909-a64c-4796-bde6-af3053c65f3b',
                                     order_type=OrderType.ORDER_TYPE_MARKET,
                                     order_id=order_id_ready,
                                     instrument_id='BBG000GQSVC2',
        )
        print(a)
# Инфо по акции
def my_shares():
    with SandboxClient(token) as client:
        a = client.instruments.share_by(
            id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_UID,
            id='6e061639-6198-4448-9568-1eadb1b0e127'
        )
        print(a.instrument.name)
        print(a.instrument.lot)
        print(a.instrument.nominal)


#tin_check()
#tin_many_in()
#post_sandbox_order()
#receiving_shares()
#user_info()
#list_transactions()
#getting_positions()
#available_balance_withdrawal()
#post_sandbox_order_sale()
#my_shares()
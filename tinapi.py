# Для подключения клиента в песочнице
from tinkoff.invest.sandbox.client import SandboxClient
from tinkoff.invest.constants import INVEST_GRPC_API_SANDBOX
# Для работы с методами клиента
from tinkoff.invest import Client
from tinkoff.invest import CandleInterval
# Для подключения сервиса из папки grpc
from tinkoff.invest.grpc.users_pb2_grpc import UsersService
from tinkoff.invest.grpc.instruments_pb2_grpc import InstrumentsService
from tinkoff.invest.grpc.sandbox_pb2_grpc import SandboxService
from tinkoff.invest.grpc.marketdata_pb2_grpc import MarketDataService
from tinkoff.invest.grpc.operations_pb2_grpc import OperationsService
#Асинхронные пакеты
import asyncio
import os
from tinkoff.invest import AsyncClient
from datetime import timedelta
from tinkoff.invest.utils import now



# Методы пишем с маленькой буквы через нижнее подчеркивание
class Tin_API:
    def __init__(self, *arg):
        self.token = arg[0]
    
    # Название тарифа
    def tin_tariff(self):
        with SandboxClient(self.token) as client:
            a = (client.users.get_info())
            return a
    #id счета
    def tin_schet(self):
        with SandboxClient(self.token) as client:
            a = (client.users.get_accounts())
            return a
    # остаток по счету
    def tin_portf(self, *arg):
        self.idaccont = arg[0]
        with SandboxClient(self.token) as client:
            a = (client.operations.get_portfolio(account_id=self.idaccont))
            return a

    # Получаем асинхронно список акций
    async def tin_req_all_shares(self):
        async with AsyncClient(self.token,
                               target=INVEST_GRPC_API_SANDBOX) as client:
            a = await client.instruments.shares()
            return a

    # Получаем асинхронно цены акций
    async def tin_req_prices_share(self, **kwarg):
        async with AsyncClient(self.token,
                               target=INVEST_GRPC_API_SANDBOX) as client:
            p = await client.market_data.get_last_prices(**kwarg)
            p1 = p.last_prices[0]
            p2 = (str(p1.price.units) + '.' + str(p1.price.nano))
            p3 = float(p2)
            p4 = round(p3, 2)
            a = (str(p4) + ' руб')
            print(a)
            return a

    # Получаем асинхронно свечи
    async def tin_req_percent(self, *arg):
        async with AsyncClient(self.token,
                               target=INVEST_GRPC_API_SANDBOX) as client:
            a = await (client.market_data.get_candles(figi=arg[0],
                                                      from_=now() - timedelta(
                                                          hours=1),
                                                      to=now(),
                                                      interval=CandleInterval.CANDLE_INTERVAL_5_MIN,
                                                      instrument_id=arg[1]))
            for b in a.candles[:-1]:
                c1 = (str(b.open.units) + '.' + str(b.open.nano))
                c2 = (str(b.close.units) + '.' + str(b.close.nano))
                c3 = float(c1)
                c4 = float(c2)
                c5 = ((1 - (c3 / c4)) * 100)
                c6 = round(c5, 2)
                c7 = (str(c6) + ' %')
                print(c7)
                if c5 >= 0:
                    c8 = (('+' + str(c6) + ' %'), '#008000')
                elif c5 < 0:
                    c8 = (c7, '#FF4500')
                return c8
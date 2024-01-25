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

from tinkoff.invest import InvestError
from tinkoff.invest import RequestError
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
            try:
                p = await client.market_data.get_last_prices(**kwarg)
            except InvestError:
                print('Ошибка в запросе цены продажи')
                err = ('Ошибка')
                return err
            p1 = p.last_prices[0]
            p2 = (str(p1.price.units) + '.' + str(p1.price.nano))
            p3 = float(p2)
            p4 = round(p3, 2)
            a = (str(p4) + ' руб')
            print(a)
            return a

    # Получаем асинхронно цены за лот
    async def tin_req_prices_lot(self, **kwarg):
        async with AsyncClient(self.token,
                               target=INVEST_GRPC_API_SANDBOX) as client:
            try:
                p = await client.market_data.get_last_prices(**kwarg)
                p1 = p.last_prices[0]
                p2 = (str(p1.price.units) + '.' + str(p1.price.nano))
                p3 = float(p2)
                a = round(p3, 2)
                print(a)
                return a
            except InvestError:
                print('Ошибка в запросе цены за лот')
                err = 0.0
                return err


    # Получаем асинхронно свечи
    async def tin_req_percent(self, *arg):
        async with AsyncClient(self.token,
                               target=INVEST_GRPC_API_SANDBOX) as client:
            try:
                a = await (client.market_data.get_candles(figi=arg[0],
                                                          from_=now() - timedelta(
                                                              hours=1),
                                                          to=now(),
                                                          interval=CandleInterval.CANDLE_INTERVAL_5_MIN,
                                                          instrument_id=arg[1]))
            except InvestError:
                print('Ошибка в запросе процента')
                err = (' - ', 'black')
                return err
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

    # Название тарифа
    def tin_brandsinfo(self):
        with SandboxClient(self.token) as client:
            a = (client.instruments.get_brands())
            return a

    #Данные для графика японских свечей
    def tin_plot_candle(self, *args):
        with Client(self.token, target=INVEST_GRPC_API_SANDBOX) as client:
            try:
                a = (client.market_data.get_candles(figi=args[0],
                                                    from_=now() - timedelta(hours=8),
                                                    to=now(),
                                                    interval=CandleInterval.CANDLE_INTERVAL_15_MIN,
                                                    instrument_id=args[1]))
                candTime = []
                openPrice = []
                maxPrice = []
                minPrice = []
                closPrice = []
                for b in a.candles[:-1]:
                    if b.is_complete:
                        openPrice.append(round((float(str(
                            b.open.units) + '.' + str(b.open.nano))), 2))
                        maxPrice.append(round((float(str(
                            b.high.units) + '.' + str(b.high.units))), 2))
                        minPrice.append(round((float(str(
                            b.low.units) + '.' + str(b.low.nano))), 2))
                        closPrice.append(round((float(str(
                            b.close.units) + '.' + str(b.close.nano))), 2))
                        candTime.append(b.time)
                return (candTime, openPrice, maxPrice, minPrice, closPrice)
            except RequestError:
                print('Ошибка при запросе свечей')
                return ([0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0])

    # Данные для линейного графика избранных акций
    def tin_plot_line(self, *args):
        with Client(self.token, target=INVEST_GRPC_API_SANDBOX) as client:
            try:
                a = (client.market_data.get_candles(figi=args[0],
                                                    from_=now() - timedelta(
                                                        days=30),
                                                    to=now(),
                                                    interval=CandleInterval.CANDLE_INTERVAL_DAY,
                                                    instrument_id=args[1]))
                candTime = []
                openPrice = []
                maxPrice = []
                minPrice = []
                closPrice = []
                for b in a.candles[:-1]:
                    if b.is_complete:
                        openPrice.append(round((float(str(
                            b.open.units) + '.' + str(b.open.nano))), 2))
                        maxPrice.append(round((float(str(
                            b.high.units) + '.' + str(b.high.units))), 2))
                        minPrice.append(round((float(str(
                            b.low.units) + '.' + str(b.low.nano))), 2))
                        closPrice.append(round((float(str(
                            b.close.units) + '.' + str(b.close.nano))), 2))
                        candTime.append(b.time)
                return (candTime, openPrice, maxPrice, minPrice, closPrice)
            except RequestError:
                print('Ошибка при запросе линейного графика')
                return ([0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0],
                        [0, 0, 0, 0])

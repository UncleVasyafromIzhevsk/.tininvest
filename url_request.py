# Для подключения клиента в песочнице
from tinkoff.invest.sandbox.client import SandboxClient
from tinkoff.invest.constants import INVEST_GRPC_API_SANDBOX
# Для работы с методами клиента
from tinkoff.invest import Client
# Для подключения сервиса из папки grpc
from tinkoff.invest.grpc.users_pb2_grpc import UsersService
from tinkoff.invest.grpc.instruments_pb2_grpc import InstrumentsService
from tinkoff.invest.grpc.sandbox_pb2_grpc import SandboxService
from tinkoff.invest.grpc.marketdata_pb2_grpc import MarketDataService
from tinkoff.invest.grpc.operations_pb2_grpc import OperationsService



# Методы пишем с маленькой буквы через нижнее подчеркивание
class UrlRequest:
    def __init__(self, *arg):
        self.token = arg[0]
    
    # Название тарифа
    def url_req_tariff(self):
        with SandboxClient(self.token) as client:
            a = (client.users.get_info())
            return a
    #id счета
    def url_req_schet(self):
        with SandboxClient(self.token) as client:
            a = (client.users.get_accounts())
            return a
    # остаток по счету
    def url_req_portf(self, *arg):
        self.idaccont = arg[0]
        with SandboxClient(self.token) as client:
            a = (client.operations.get_portfolio(account_id=self.idaccont))
            return a

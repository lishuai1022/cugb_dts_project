from ..config import config
from ..dts import Dts
from ..daos.TraderDao import TraderDao
from ..error import *

#下单模型
class OrderModel():
    #初始化
    def __init__(self,trader_id):
        traderdao = TraderDao()
        trader_info = traderdao.getTraderAccount(trader_id)
        if trader_info is None \
                or trader_info['securit'] is None \
                or len(trader_info['securit'])==0:
            raise error_api_data_error
        self.dts_client = Dts(trader_info['account'],trader_info['securit'],config.DTS_DOMAIN)
    #下单
    def placeorder(self,data):
        source = data['source']
        code = data['code']
        price = data['price']
        count = data['count']
        otype = int(data['otype'])
        ptype = int(data['ptype'])
        public = int(data['public'])
        try:
            return self.dts_client.order(source,code, price, count, otype, ptype, public)
        except Exception as e:
            raise e

    #撤单
    def cancelorder(self,order):
        try:
            return self.dts_client.cancel(order)
        except Exception as e:
            raise e


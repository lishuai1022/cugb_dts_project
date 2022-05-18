from ... import access, forms
from ...error import *
from ..AuthHandler import AuthHandler
import time,datetime
from ...daos.OrderDao import *
import math
from ...daos.BScountDao import *

class StockBscountHandler(AuthHandler):
    @access.exptproc
    def get(self):
        trader_id = self.trader_id
        ccode = self.get_argument('ccode','')
        faccount_id = self.get_argument('faccount_id','')
        price = self.get_argument('price','')
        if price == '' or ccode == '' or faccount_id == '':
            raise invalid_parameters
        source = self.get_argument('source', '0')
        if source not in ['0', '1']:
            source = '0'

        #价格判断
        if not checkPrice(price):
            raise price_error

        bscountdao = BScountDao()
        if source == '1':
            traderinfo = self.traderinfo
            try:
                trader_config = json.loads(traderinfo['configs'])
                public_stock = '0'
                if 'public_stock' in trader_config.keys():
                    public_stock = trader_config['public_stock']
            except:
                raise Exception('trader data error')
            if int(public_stock) != 1:
                raise trd_no_public_access_error

        data = bscountdao.getBscount(source,trader_id,faccount_id,ccode,price)
        self.write(protocol.success(data=data))
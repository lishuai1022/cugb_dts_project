from ... import access, forms,protocol
from ..AuthHandler import AuthHandler
from ...error import *
from ...util import checkInput
from ...models.OrderModel import OrderModel
from ...daos.OrderDao import OrderDao
from ...daos.TraderDao import TraderDao
from decimal import Decimal
from ...util.OrderHelp import OrderHelp
from ...util.checkInput import batchGetStockHq
import logging,json

import time

class OrderHandler(AuthHandler):
    # @tornado.web.asynchronous
    # @tornado.gen.coroutine
    @access.exptproc
    def post(self):

        ######################## 参数验证B ########################
        form = forms.stock.Buy(**self.arguments)
        trader_id = self.trader_id
        ccode = form['ccode']
        tside = int(form['tside'])
        faccount_id = int(form['faccount_id'])
        quantity = int(form['quantity'])
        price = float(form['price'])
        self.faccount_id = faccount_id
        source = self.get_argument('source', '0')
        if source not in ['0', '1']:
            source = '0'

        try:
            quantity = int(self.arguments['quantity'])
        except:
            raise invalid_parameters

        if tside == 0 and quantity % 100 != 0:
            raise quantity_error

        req_data = {
            'source':faccount_id,
            'code':ccode,
            'price':price,
            'count':quantity,
            'otype':tside,
            'ptype':0,
            'public':source,
        }
        orderModel = OrderModel(trader_id)

        try:
            order_id = orderModel.placeorder(req_data)
            self.write(protocol.success(status='0', msg='下单委托成功', data={"order_id": order_id}))
        except Exception as e:
            self.write(protocol.success(e.status, e.msg))
        self.finish()
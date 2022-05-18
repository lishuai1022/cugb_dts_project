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

class BatchOrderHandler(AuthHandler):
    # @tornado.web.asynchronous
    # @tornado.gen.coroutine
    @access.exptproc
    def post(self):

        ######################## 参数验证B ########################
        trader_id = self.trader_id
        tside = self.get_argument('tside','')
        orderinfo = self.get_argument('orderinfo','')
        if len(str(tside)) == 0:
            raise missing_parameters
        if len(str(orderinfo)) == 0:
            raise missing_parameters

        try:
            quantity = json.loads(orderinfo)
        except:
            raise invalid_parameters

        orderModel = OrderModel(trader_id)
        res_msg = {'success':[],'error':[]}
        for order in orderinfo:
            req_data = {
                'source':order['faccount_id'],
                'code':order['ccode'],
                'price':'',
                'count':order['count'],
                'otype':tside,
                'ptype':0
            }
            order_id = 0
            try:
                order_id = orderModel.placeorder(req_data)
                res_msg['success'].append({'order_id':order_id,'faccount_id':req_data['source'],'ccode':req_data['code']})
            except Exception as e:
                res_msg['error'].append({'faccount_id': req_data['source'], 'ccode': req_data['code'],'error_msg':'%s_%s' % (e.status,e.msg)})

        if len(res_msg['error']) == 0: #全部成功
            self.write(protocol.success(status='0', msg='下单委托成功', data=res_msg))
        else:#未全部成功
            self.write(protocol.success(status='-999',msg='下单未全部委托成功',data=res_msg))
        self.finish()




from ... import access, forms
from ...error import *
from ..AuthHandler import AuthHandler
from ...error import *
from ...models.OrderModel import OrderModel
from ...daos.OrderDao import OrderDao
import time,json
from ...util import checkInput
import logging

class CancelHandler(AuthHandler):
    @access.exptproc
    def post(self):
        form = forms.order.Cancel(**self.arguments)
        trader_id = self.trader_id
        order_id = form['order_id']

        ########################## 风控S ##########################
        # # 1.获取交易员状态信息
        # trader_status = self.traderinfo['status']
        # if trader_status == 'blimit':
        #     raise risk_blimit_error
        # elif trader_status == 'bslimit':
        #     raise risk_bslimit_error
        # elif trader_status == 'disable':
        #     raise risk_disable_error
        #
        # # 2.获取配置信息
        # config_list = [
        #     'number_limit',  # 下单数量上限
        #     'money_limit',  # 下单金额上限
        #     'holiday_list',  # 非周末节假日列表
        #     'trade_time_period',  # 交易时间段
        #     'single_max_credit',  # 单券最大头寸
        #     'sum_max_credit',  # 账户累计最大头寸
        #     'single_max_loss',  # 单券最大亏损
        #     'sum_max_loss',  # 账户累计最大亏损
        # ]
        # orderdao = OrderDao()
        # clist = orderdao.getConfiginfo(config_list)
        #
        # # 交易日期
        # now_mill_timestamp = int(time.time() * 1000)
        # today = time.strftime("%Y-%m-%d", time.localtime(now_mill_timestamp / 1000))
        # if today in clist['holiday_list']:
        #     raise risk_trade_date
        #
        # # 交易时间
        # now_time = time.strftime("%H:%M:%S", time.localtime(now_mill_timestamp / 1000))
        # trade_time_period = json.loads(clist['trade_time_period'])
        #
        # if now_time < trade_time_period['m_start'] \
        #         or now_time > trade_time_period['a_end'] \
        #         or (now_time > trade_time_period['m_end'] and now_time < trade_time_period['a_start']):
        #     raise risk_trade_time
        ########################## 风控E ##########################
        # #更改可撤订单状态
        # order_list = orderdao.getBatchCancelOrder(trader_id, order_id)
        # if order_list == [] or order_list == ():
        #     raise trd_no_valid_order
        # 
        # orderdao.updateBatchCancelOrder(trader_id,order_id)

        # order_id_str = ''
        # for o in order_list:
        #     if o['ocode'] is None or o['ocode']=='':
        #         continue
        #     order_id_str += o['ocode']
        # if order_id_str == '':
        #     self.write(protocol.success(status='0', msg='撤单成功', data={}))
        #     return

        # req_data = {
        #     'trader_id': trader_id,
        #     'cli_oid': order_id
        # }

        orderModel = OrderModel(trader_id)
        try:
            res = orderModel.cancelorder(order_id)
            print(res)
            r_success = 0
            success_orderids = []
            r_error = 0
            error_orderids = []
            for r in res:
                if int(r['status']) == 0:
                    r_success += 1
                    success_orderids.append(r['order'])
                else:
                    r_error += 1
                    error_orderids.append(r['order'])
            if r_success == len(res):
                msg = '撤单委托成功'
                self.write(protocol.success('0', msg, data={"order_id": order_id}))
            elif r_error == len(res):
                msg = '撤单委托失败'
                self.write(protocol.success('0', msg, data={}))
            else:
                msg = '部分撤单委托成功'
                success_orders = ','.join(success_orderids)
                # error_orders = ','.join(error_orderids)
                self.write(protocol.success('0', msg, data={"order_id": success_orders}))
        except Exception as e:
            self.write(protocol.success(e.status, e.msg))
        self.finish()
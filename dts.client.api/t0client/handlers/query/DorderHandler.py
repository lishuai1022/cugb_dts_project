from ... import access, forms
from ...error import *
from ..AuthHandler import AuthHandler
from ...daos.OrderDao import OrderDao
from ...daos.PerformDao import PerformDao
from decimal import Decimal

class DorderHandler(AuthHandler):
    @access.exptproc
    def get(self):
        item = self.get_argument('item', '')

        performdao = PerformDao()
        datalist = performdao.getTraderDailyOrder2(self.trader_id, item)
        resdata = []
        item_cancel_flag = True if item.find('can_cancel') >= 0 else False #是否包含可撤订单筛选项
        for dt in datalist:
            dprice = dt['dprice'] if dt['dprice'] is not None else 0.00
            dcount = dt['dcount'] if dt['dcount'] is not None else 0

            dt['dmoney'] = str(Decimal(dprice * dcount).quantize(Decimal('0.00')))
            dt['fee'] = dt['cost']
            if dt['status'] in ['unsend','tosend','sending','sent','pdealt']:#可撤订单条件判断
                dt['cancel_flag'] = 1 if int(dt['clear']) == 0 else 0
                if item_cancel_flag and dt['cancel_flag'] == 0:#不可撤
                    continue
            else:
                dt['cancel_flag'] = 0

            resdata.append(dt)

        data = {

            "list": resdata
        }
        self.write(protocol.success(data=data))
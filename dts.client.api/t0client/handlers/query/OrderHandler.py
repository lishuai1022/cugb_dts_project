from ... import access, forms
from ...error import *
from ..AuthHandler import AuthHandler
from ...daos.OrderDao import OrderDao
from decimal import Decimal
from ...config import pubconf
import time

class OrderHandler(AuthHandler):
    @access.exptproc
    def get(self):
        page = self.get_argument('page', 1)
        pagesize = self.get_argument('pagesize', 10)
        faccount_id = self.get_argument('faccount_id', '')
        ccode = self.get_argument('ccode', '')
        side = self.get_argument('side', '')
        sdate = self.get_argument('sdate', '')
        edate = self.get_argument('edate', '')
        source = self.get_argument('source','0')
        if source not in ['0','1','2']:
            source = '0'

        sort = self.get_argument('sort', 'order_id')
        order = self.get_argument('order', 'desc')
        field_list = [
            "order_id",
            "ccode",
            "cname",
            "fname",
            "source",
            "ocode",
            "side",
            "status",
            "otype",
            "oprice",
            "ocount",
            "dprice",
            "dcount",
            "dmoney",
            "cost",
            "amount",
            "otime",
            "dtime",
            "type",
        ]
        if sort not in field_list:
            sort = 'order_id'
        if order not in ['asc', 'desc', 'ASC', 'DESC']:
            order = 'desc'

        orderdao = OrderDao()
        total = orderdao.getAllOrderListTotal(self.trader_id,faccount_id,ccode,side,sdate,edate,source)
        datalist = orderdao.getAllOrderList(self.trader_id,faccount_id,ccode,side,sdate,edate,page,pagesize,True,source,sort,order)
        for dt in datalist:
            dprice = dt['dprice'] if dt['dprice'] is not None else 0.00
            dcount = dt['dcount'] if dt['dcount'] is not None else 0

            dt['dmoney'] = str(Decimal(dprice * dcount).quantize(Decimal('0.00')))
            dt['odate'] = str(dt['odate'])
            dt['otime'] = time.strftime("%H:%M:%S", time.localtime(dt['otime'] / 1000))
            dt['side'] = '买入' if dt['side'] == 0 else '卖出'
            dt['status'] = pubconf.ORDER_STATUS[dt['status']]
            dt['oprice'] = str(dt['oprice'])
            dt['dprice'] = str(dt['dprice']) if dt['dprice'] is not None else '--'
            dt['dcount'] = str(dt['dcount']) if dt['dcount'] is not None else '--'
            dt['dmoney'] = str(dt['dmoney']) if dt['dmoney'] != 0.00 else '--'
            dt['type'] = "虚拟委托" if dt['type'] == 1 else '--'
            dt['ocode'] = dt['ocode'] if dt['ocode'] is not None else '--'

        data = {
            "total": total,
            "page": page,
            "pagesize": pagesize,
            "list": datalist
        }
        self.write(protocol.success(data=data))
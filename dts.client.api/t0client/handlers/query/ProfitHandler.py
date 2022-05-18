from ... import access, forms
from ...error import *
from ..AuthHandler import AuthHandler
from ...daos.TQuerydao import *
from ...daos.OrderDao import OrderDao

class ProfitHandler(AuthHandler):
    @access.exptproc
    def get(self):
        page = self.get_argument('page', 1)
        pagesize = self.get_argument('pagesize', 10)
        faccount_id = self.get_argument('faccount_id', '')
        ccode = self.get_argument('ccode', '')
        sdate = self.get_argument('sdate', '')
        edate = self.get_argument('edate', '')
        source = self.get_argument('source', '0')
        if source not in ['0', '1', '2']:
            source = '0'

        sort = self.get_argument('sort','odate')
        order = self.get_argument('order','desc')
        field_list = [
            "odate",
            "ccode",
            "cname",
            "fname",
            "tprofit",
            "interest",
            "profit",
            "source",
        ]
        if sort not in field_list:
            sort = 'odate'
        if order not in ['asc','desc','ASC','DESC']:
            order = 'desc'


        orderdao = OrderDao()
        res = orderdao.getTraderProfitListTotal(self.trader_id,faccount_id,ccode,sdate,edate,source)
        datalist = orderdao.getTraderProfitList(self.trader_id,faccount_id,ccode,sdate,edate,page,pagesize,True,source,sort,order)


        data = {
            "total":res['total'],
            "sum_profit":res['sum_profit'],
            "page":page,
            "pagesize":pagesize,
            "list":datalist
        }
        self.write(protocol.success(data=data))
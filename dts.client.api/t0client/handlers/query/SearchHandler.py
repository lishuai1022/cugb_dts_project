from ... import access, forms
from ...error import *
from ..AuthHandler import AuthHandler
import time,datetime
from ...daos.OrderDao import *

class SearchHandler(AuthHandler):
    @access.exptproc
    def get(self):
        keyword = self.get_argument('keyword', '')
        faccount_id = self.get_argument('faccount_id', '')


        orderdao = OrderDao()
        res = orderdao.searchStock(self.trader_id,keyword,faccount_id)
        self.write(protocol.success(data=res))
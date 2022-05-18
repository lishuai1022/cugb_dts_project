from ... import access, forms
from ...error import *
from ..AuthHandler import AuthHandler
import time,datetime
from ...daos.OrderDao import *

class FaccountListHandler(AuthHandler):
    @access.exptproc
    def get(self):

        orderdao = OrderDao()
        res = orderdao.getFaccountList(self.trader_id)
        self.write(protocol.success(data=res))
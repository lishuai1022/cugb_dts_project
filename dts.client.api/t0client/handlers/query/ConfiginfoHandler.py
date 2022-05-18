from ... import access, forms
from ...error import *
from ..AuthHandler import AuthHandler
from ...daos.OrderDao import *

class ConfiginfoHandler(AuthHandler):
    @access.exptproc
    def get(self):
        orderdao = OrderDao()
        res = orderdao.getConfiginfo([
            "money_limit",
            "number_limit"])
        self.write(protocol.success(data=res))
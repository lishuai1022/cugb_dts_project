from ... import access, forms
from ..OpenHandler import *
from ...error import *
from ...daos.TraderDao import *
from ...util.checkInput import *

class CheckHandler(OpenHandler):
    """
        判断用户是否登录
    """
    @access.exptproc
    def get(self):
        account = self.get_argument('account','')
        if account == '':
            raise missing_parameters

        #获取账户信息
        traderDao = TraderDao()
        trader_info = traderDao.getInfoByAccount(account)
        if trader_info is None:
            data = {
                'login': 0,
            }
            self.write(protocol.success(data=data))
            return

        trader_id = trader_info['id']
        # 前端token
        client_key = self.getUserTokenKey(trader_id)
        client_token = self.redis.get(client_key)
        if client_token is None or client_token == '':
            login = 0
        else:
            login = 1
        data = {
            'login':login,
        }
        self.write(protocol.success(data=data))


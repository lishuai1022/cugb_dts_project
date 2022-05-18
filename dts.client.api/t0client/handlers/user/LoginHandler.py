from ... import access, forms
from ..OpenHandler import *
from ...error import *
from ...daos.TraderDao import *
from ...util.checkInput import *

class LoginHandler(OpenHandler):
    """
        用户登录
    """
    @access.exptproc
    def post(self):
        form = forms.login.Login(**self.arguments)

        #验证码
        type = '0'  # 登录
        img_code = self.get_argument('imgcode', '')
        img_code_key = CAPTCHA_CODE_REDIS_PREFIX + type
        img_code_time_key = CAPTCHA_TIME_REDIS_PREFIX + type
        cur_time = int(time.time())

        if img_code_key not in self.session or img_code_time_key not in self.session:
            raise error_imgcode_expire_exception

        if self.session[img_code_time_key] + CAPTCHA_TIMEOUT < cur_time:
            raise error_imgcode_expire_exception

        if self.session[img_code_key].lower() != img_code.lower():
            raise error_imgcode_valid_exception

        #获取账户信息
        traderDao = TraderDao()
        trader_info = traderDao.verifyPwd(self.arguments['account'],self.arguments['pwd'])
        if trader_info is None:
            raise error_pwd_valid_exception
        if trader_info['delete'] == '0':
            raise error_account_exception

        trader_id = trader_info['id']
        trader_name = trader_info['name']
        # 前端token
        client_key = self.getUserTokenKey(trader_id)
        client_token = self.generateToken(trader_id)
        self.redis.set(client_key, client_token, 3600 * 12)


        data = {
            'trader_id':trader_id,
            'account':form.account,
            "token":client_token,
            "trader_name":trader_name
        }
        self.write(protocol.success(data=data))


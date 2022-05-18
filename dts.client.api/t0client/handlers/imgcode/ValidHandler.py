from ... import access
from ...error import *
from ..OpenHandler import OpenHandler
import time
from ...config.config import *

class ValidHandler(OpenHandler):
    @access.exptproc
    def post(self):
        """校验图片验证码"""
        type = '0' #登录
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

        self.write(protocol.success())
import time
from ... import access, forms
from ..OpenHandler import OpenHandler
from ...util.captcha import *
try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

class GetHandler(OpenHandler):
    @access.exptproc
    def get(self):
        type = '0' #注册
        img_code_key = CAPTCHA_CODE_REDIS_PREFIX + type
        img_code_time_key = CAPTCHA_TIME_REDIS_PREFIX + type
        cur_time = int(time.time())
        image, code = create_validate_code()

        out = BytesIO()
        image.save(out, format='png')
        out.seek(0)

        self.session[img_code_key] = code
        self.session[img_code_time_key] = cur_time
        self.session.save()

        self.set_header('Content-Type', 'image/png;')
        self.write(out.getvalue())
        self.finish()
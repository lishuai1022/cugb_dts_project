from __future__ import with_statement
import tornado.web
from tornado.escape import json_decode
# from config.commconf import *
from ...config import *

from .RegBaseHandler import *



class SessionHandler(RegBaseHandler):
    def get(self):

        data = {
            'status': 0,
            'data': {
                "session_id" : self.session.session_id,
                # "verification" : self.session.hmac_key,
                # "pop_num" : PHONE_CODE_NUM_USEIMG
            }
        }
        self.respond_data(data)
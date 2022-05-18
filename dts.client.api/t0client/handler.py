"""
    base handler
"""
import tornado.web
from . import config
from .util import *
from .config.config import *
import time


class Handler(tornado.web.RequestHandler):
    """
        base handler for request handlers
    """
    def initialize(self):
        """
            overwrite: initialize
        :return:
        """
        super(Handler, self).initialize()
        self.redis = self.application.redis
        self.session = session.Session(self.application.session_manager, self)

    def set_default_headers(self):
        """
            overwrite: set default headers
        :return:
        """
        for header in config.HEADERS:
            self.set_header(*header)

    @property
    def arguments(self):
        args = {}
        for arg in self.request.arguments.keys():
            args[arg] = self.get_argument(arg)
        return args

    @property
    def cleaned_arguments(self):
        args = {}
        for arg in self.request.arguments.keys():
            if not arg.startswith('_'):
                args[arg] = self.get_argument(arg)
        return args

    def getUserTokenKey(self, trader_id):
        return CLIENT_TOKEN_KEY_PREFIX + str(trader_id)

    def generateToken(self, trader_id):
        cur_time = int(round(time.time() * 1000))
        seed = str(cur_time) + '_' + str(trader_id) + '_' + CLIENT_TOKEN_AUTH_KEY
        return self.md5(seed)

    # def getBackendToken(self,tacctount_id):
    #     return self.redis.get(BACKEND_TOKEN_KEY_PREFIX + str(tacctount_id))

    def md5(self, str):
        import hashlib
        m = hashlib.md5()
        m.update(str.encode('utf-8'))
        return m.hexdigest()

    def respond_data(self, data):
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.write(data)
        self.finish()

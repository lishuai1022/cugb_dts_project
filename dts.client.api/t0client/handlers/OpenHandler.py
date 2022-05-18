
from .. import handler
from ..models.ApiModel import *
from ..config.config import *


class OpenHandler(handler.Handler):

    def initialize(self):
        super().initialize()
        self.apiModel = ApiModel()
        self.traderapi_hash = TRADE_REDIS_HASH


    # def respond_data(self, data):
    #     self.set_header('Content-Type', 'application/json; charset=UTF-8')
    #     self.write(data)
    #     self.finish()

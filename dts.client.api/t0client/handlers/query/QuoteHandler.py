from ... import access, forms
from ...error import *
from ..AuthHandler import AuthHandler
import time,datetime,json
from ...util.hq import *
from ...config.pubconf import hq_key

class QuoteHandler(AuthHandler):
    @access.exptproc
    def get(self):
        # time1 = time.time() * 1000

        code = self.get_argument('code','')
        try:
            hq_client = Hq(hq_key)
            # 单个股票实时价格
            res = hq_client.single_stock_price(code)

            # time2 = time.time() * 1000
            # import logging
            # time3 = time2-time1
            # logging.info(time1)
            # logging.info(time2)
            # logging.info(time3)
        except Exception as e:
            raise error_hq_service_exception

        self.write(protocol.success(data=res))


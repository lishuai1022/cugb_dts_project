import requests,logging,traceback
from .BaseModel import BaseModel
from ..error import *
from ..token import *
import time,json,tornado.gen,tornado.httpclient
from urllib.parse import urlencode
from ..access import *

def doapi(handler_func):
    def wrapper(self, *args, **kwargs):
        try:
            args[1]['tm'] = str(int(round(time.time() * 1000)))
            args[1]['sign'] = getSign(args[1])
            return handler_func(self, *args, **kwargs)
        except Exception :
            logging.error(traceback.format_exc())
            return error_api_data_exception.data
    return wrapper

class ApiModel(BaseModel):

    @tornado.gen.coroutine
    def AsynPost(self,url,params):
        body = urlencode(params)

        request = tornado.httpclient.HTTPRequest(url=url, method="POST", body=body)
        http_client = tornado.httpclient.AsyncHTTPClient()
        response = yield tornado.gen.Task(http_client.fetch, request)
        data = json.loads(response.body.decode())

        saveMsg(data)

        raise tornado.gen.Return(data)

    def orderPlace(self, params):
        url = self.domain + self.url_config['TRADE_ORDER_PLACE']
        params['btype'] = 'dts'
        params['tm'] = str(int(round(time.time() * 1000)))
        params['sign'] = getSign(params)

        print(url,params)

        return self.AsynPost(url,params)

    def orderCancel(self, params):
        url = self.domain + self.url_config['TRADE_ORDER_CANCEL']
        params['btype'] = 'dts'
        params['tm'] = str(int(round(time.time() * 1000)))
        params['sign'] = getSign(params)
        # print(url)
        # print(params)
        return requests.post(url,params).json()
        # return self.AsynPost(url,params)

    @doapi
    def getData(self,url,params={}):
        print(url,params)
        logging.info(url + '?' + urlencode(params))
        res = requests.post(url,params).json()
        logging.info(res)
        return res

    # def orderCancel(self, params={}):
    #     return self.getData(self.domain + self.url_config['TRADE_ORDER_CANCEL'], params)


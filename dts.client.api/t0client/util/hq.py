# -*- coding:utf-8 -*-
import os
import datetime
import time
import hashlib
import decimal
import requests
import logging
import traceback
import threading
"""
行情系统同步SDK
依赖模块：requests
"""

class HqException(Exception):
    """
    行情异常类，使用方需捕获该异常
    """
    def __init__(self, status=-1, msg='请求异常，请检查'):
        self._status = status
        self._msg = msg

    @property
    def status(self):
        return self._status

    @property
    def msg(self):
        return self._msg

    def __str__(self):
        return 'status: ' + str(self._status) + ', msg: ' + self._msg



class Hq():
    """
    The api of hq.
    """
    _HOST = 'http://sq.youlikj.com'
    _TIMEOUT = 10
    _OPEN_LOG = True

    def __init__(self, skey:str, host:str = _HOST, timeout = _TIMEOUT, open_log = _OPEN_LOG):
        """
        构造函数
        :param skey: 分配加密密钥
        :param host: 远程服务域名
        :param timeout: 远程服务超时时间(连接时间、读取时间)
        :return: 
        """
        self._skey = skey
        self._host = host
        self._timeout = timeout
        self._open_log = open_log


    def _dts_wrap(func):    
        def _runtime(self, *args, **kwargs):
            d = datetime.datetime.now()
            st = time.time()
            result = func(self, *args,**kwargs)
            et = time.time()
            
            if self._open_log:
                logging.info('cur_time:{},func:{}, start_time:{},exec_time:{}'.format(d.strftime('%Y-%m-%d %H:%M:%S'), func.__name__, st, et-st))
            return result
         
        return _runtime


    @_dts_wrap
    def single_stock_price(self, code: str):
        """
        股票五档行情
        :param code: 证券代码
        :return:
        """
        uri = '/stock/price'
        data = {
            'code': code,
        }
        result = self._request(method='get', uri=uri, data=data)
     
        return result
    
    @_dts_wrap 
    def batch_stock_price(self, codes: str):
        """
        批量查询股票当前价格
        :param codes: 股票代码集合，使用","连接
        :return:
        """
        uri = '/batch/stock/price'
        data = {
            "codes": codes,
        }
        result = self._request(method='get', uri=uri, data=data)

        return result


    @staticmethod
    def _price(money):
        return decimal.Decimal(money).quantize(decimal.Decimal('0.00'))

    @staticmethod
    def _quantity(quantity):
        return int(quantity)

    def _get_token(self, data: dict):
        """
        获取输入参数集的MD5码
        :param data: dict, 输入的参数集
        :return: 计算出的MD5码
        """
        _val = str(data['timestamp']) + '&' + self._skey
        return hashlib.md5(_val.encode(encoding='UTF-8')).hexdigest()

    def _request(self, method: str, uri: str, data: dict):
        """
        发起Http方式请求服务
        :param method: str, 请求方式，[get, post]
        :param uri: str, 请求的服务地址，不包含主机地址
        :param data: dict, 请求参数集合
        :return: 成功时返回结果集，失败时返回None
        """
        try:
            data['timestamp'] = int(time.time())
            data['sign'] = self._get_token(data=data)
            url = self._host + uri
            # print(url)
            # print(data)
            result = requests.request(method=method, url=url, params=data, timeout=(self._timeout, self._timeout))
            # print(result)

            if isinstance(result, requests.models.Response):
                if (result.status_code == requests.codes.ok):
                    result = result.json()
                    # print(result)
                    if str(result['status']) != '0':
                        raise HqException(int(result['status']), result['msg'])
                    else:
                        return result['data']
                else:
                    raise HqException(result.status_code, result.reason)

            else:
                raise HqException()

        except requests.exceptions.Timeout as e:
            raise HqException(-504, 'timeout')

        except HqException as e:
            raise HqException(e.status, e.msg)

        except Exception as e:
            msg = traceback.format_exc()
            logging.info(msg)
            raise HqException(-1, str(e))




if __name__ == '__main__':
    """
    调用demo
    """
    hq_client = Hq('s2q4y3er', 'http://127.0.0.1:50100')
    #单个股票实时价格
    result = hq_client.single_stock_price('601288')
    print(result)
    #多个股票实时价格
    result = hq_client.batch_stock_price('000001,601288')
    print(result)
   
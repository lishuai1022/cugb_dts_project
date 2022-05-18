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
交易系统SDK
依赖模块：requests
"""

class DtsException(Exception):
    """
    dts异常类，使用方需捕获该异常
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



class Dts():
    """
    The api of dts.
    """
    _HOST = 'https://open.dts.youlikj.com'
    _TIMEOUT = 10
    _OPEN_LOG = True

    def __init__(self, account:str, skey:str, host:str = _HOST, timeout = _TIMEOUT, open_log = _OPEN_LOG):
        """
        构造函数
        :param account: 分配的交易员账号code
        :param skey: 分配加密密钥
        :param host: 远程服务域名
        :param timeout: 远程服务超时时间(连接时间、读取时间)
        :return: 
        """
        self._account = account
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
    def order(self, source: str, code: str, price: str, count, otype: int, ptype = 0, public = 0):
        """
        下单接口，包括买单和卖单
        :param source: 券源标识
        :param code: 证券代码
        :param price: 委托价格
        :param count: 委托数量
        :param otype: 交易类型：0-买入，1-卖出
        :param ptype: 价格类型：0-限价
        :param ptype: 公共券源: 0-否，1-是
        :return: 成功时返回订单编号，失败时返回None
        """

        uri = '/stock/order/place'
        data = {
            'source': source,
            'code': code,
            'price': price,
            'count': count,
            'otype': otype,
            'ptype': ptype,
            'public': public,
        }
        result = self._request(method='get', uri=uri, data=data)

        if result is not None:
            result = result['order']
        return result

    @_dts_wrap
    def cancel(self, order):
        """
        撤单接口
        :param order: 订单编号
        :return:
        """
        uri = '/stock/order/cancel'
        data = {
            'order': order,
        }
        result = self._request(method='get', uri=uri, data=data)

        # if result is not None:
        #     result = result['order']
        return result

    @_dts_wrap
    def query(self, category: int, code = None,  order=None):
        """
        查询交易
        :param category:查询类别：0-查询资金余额，1-查询持仓股票，2-查询当日委托，3-查询成交明细
        :param code: str, 证券代码，category为1时必填，为""时查询所有记录
        :param order: 委托编号：category为2时必填，为""时查询当日所有记录，category为3时必填，不可为“”
        :return:
        """

        if category == 0:
            return self._query_asset(category)
        elif category == 1:
            if code is None:
                return None
            return self._query_position(category, code)

        elif category == 2:
            if order is None:
                return None
            return self._query_order(category, order)

        if category == 3:
            if order in (None, ""):
                return None
            return self._query_deal(category, order)

    def _query_asset(self, category: int):
        """
        查询资金余额
        :param category: 查询类别：0-查询资金余额
        :return:
        """
        uri = '/stock/query'
        data = {
            'category': category,
        }
        result = self._request(method='get', uri=uri, data=data)
        if result is not None:
            result['asset'] = self._money(result['asset'])
            result['value'] = self._money(result['value'])
            result['available'] = self._money(result['available'])
            result['frozen'] = self._money(result['frozen'])
        return result
        
    def _query_position(self, category: int, code: str):
        """
        查询用户的持仓
        :param category: 查询类别：1-查询持仓股票
        :param code: 股票代码
        :return:
        """
        uri = '/stock/query'
        data = {
            "category" : category,
            "code": code,
        }
        result = self._request(method='get', uri=uri, data=data)
        if result is not None:
            # result = result['list']
            for position in result:
                position['source'] = position['source']
                position['code'] = position['code']
                position['hold'] = self._quantity(position['hold'])
                position['left'] = self._quantity(position['left'])

        return result


    def _query_order(self, category: int, order):
        """
        查询当日委托
        :param category: 2-查询当日委托
        :param order: 订单编号
        :return:
        """
        uri = '/stock/query'
        data = {
            'category': category,
            'order': order,
        }
        result = self._request(method='get', uri=uri, data=data)
        if result is not None:
            for order in result:
                order['order'] = order['order']
                order['code'] = order['code']
                order['otype'] = int(order['otype'])
                order['ptype'] = int(order['ptype'])
                order['status'] = order['status']
                order['ocount'] = self._quantity(order['ocount'])
                order['oprice'] = self._money(order['oprice'])
                order['otime'] = int(order['otime'])
                order['dcount'] = self._quantity(order['dcount']) if order['dcount'] is not None else None
                order['dprice'] = self._money(order['dprice']) if order['dprice'] is not None else None
                order['dtime'] = int(order['dtime']) if order['dtime'] is not None else None
        return result

    def _query_deal(self, category: int,  order):
        """
        查询成交明细
        :param category: 3-查询成交明细
        :param order: 订单编号
        :return:
        """
        uri = '/stock/query'
        data = {
            'category': category,
            'order': order,
        }
        result = self._request(method='get', uri=uri, data=data)
        if result is not None:
            for deal in result:
                deal['order'] = deal['order']
                deal['dealt'] = int(deal['dealt'])
                deal['code'] = deal['code']
                deal['otype'] = int(deal['otype'])
                deal['dcount'] = self._quantity(deal['dcount'])
                deal['dprice'] = self._money(deal['dprice'])
                deal['dmoney'] = self._money(deal['dmoney'])
                deal['dtime'] = int(deal['dtime'])
        return result

    @staticmethod
    def _money(money):
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
        _val = self._skey + ''.join([str(v) for k, v in sorted(data.items()) if (k != 'sign') and (v is not None)])
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
            data['tm'] = int(time.time() * 1000)
            data['account'] = self._account
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
                        raise DtsException(int(result['status']), result['msg'])
                    else:
                        return result['data']
                else:
                    raise DtsException(result.status_code, result.reason)

            else:
                raise DtsException()

        except requests.exceptions.Timeout as e:
            raise DtsException(-504, 'timeout')

        except DtsException as e:
            raise DtsException(e.status, e.msg)

        except Exception as e:
            msg = traceback.format_exc()
            logging.info(msg)
            raise DtsException(-1, str(e))




if __name__ == '__main__':
    """
    调用demo
    """
    dts_client = Dts('moni01', 'c7e0e8cbdb3cbb5c6275e4ab068b9615')
    #下单
    order_id = dts_client.order(1,'601288', '3.6', 1000, 0)
    print(order_id)
    #撤单
    order_id = dts_client.cancel('8220')
    print(order_id)
    #查询资金余额
    result = dts_client.query(0)
    print(result)
    #查询持仓股票
    result = dts_client.query(1, code = "")
    print(result)
    #查询当日委托
    result = dts_client.query(2, order = "")
    print(result)
    #查询成交明细
    result = dts_client.query(3, order = '1564363521197')
    print(result)

#!/usr/bin/python
# -*- coding:utf-8 -*-
'''
订单相关辅助方法
'''
# import random
# import time, datetime, requests
# from tornado.escape import json_decode
from decimal import Decimal, ROUND_HALF_UP
# from .. import config


class OrderHelp(object):

    def dc2(val):
        return Decimal(str(val)).quantize(Decimal('0.00'), ROUND_HALF_UP)

    def dc10(val):
        return Decimal(str(val)).quantize(Decimal('0.0000000000'), ROUND_HALF_UP)

    def getHfeeAndAmount(order):
        '''
            根据订单信息，获取委托占用金额 和 费用
            oprice ocount tfee rfee stax side
        '''
        price = order['oprice']
        count = order['ocount']
        if count is None or count == 0:
            return OrderHelp.dc2('0'), OrderHelp.dc2('0')

        amount = price * count
        tfee_val = OrderHelp.dc2(amount * float(order['tfee']))
        rfee_val = OrderHelp.dc2(max(amount * float(order['rfee']), float(order['mfee'])))
        if order['side'] == 1:
            stax_val = OrderHelp.dc2(amount * float(order['stax']))
            hfee = tfee_val + rfee_val + stax_val
            amount = amount - float(hfee)
        else:
            hfee = tfee_val + rfee_val
            amount = amount + float(hfee)

        return OrderHelp.dc2(amount), OrderHelp.dc2(hfee)

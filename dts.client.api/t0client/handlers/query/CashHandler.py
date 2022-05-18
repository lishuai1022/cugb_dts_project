from ... import access, forms
from ..AuthHandler import AuthHandler
from ...daos.OrderDao import *
from ...daos.PerformDao import PerformDao
from ...util.checkInput import batchGetStockHqFromQuote,getuniqlist
import json,datetime

class CashHandler(AuthHandler):
    '''获取头寸列表 头寸=历史头寸+当日头寸'''
    @access.exptproc
    def get(self):
        performdao = PerformDao()
        # 获取交易底仓的所有股票
        cash_list = performdao.getTraderProfitList(self.trader_id)

        if len(cash_list) > 0:
            uniq_ccode_list = list(set([p['ccode'] for p in cash_list]))
            # 获取行情
            quote_dict = batchGetStockHqFromQuote(uniq_ccode_list)

            for c in cash_list:
                c['float_profit'] = Decimal(c['cash_count'] * (float(quote_dict[c['ccode']]) - float(c['ori_price']))).quantize(Decimal('0.00'))

        data = {'list': cash_list}
        self.write(protocol.success(data=data))

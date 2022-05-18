from ... import access, forms
from ...error import *
from ..AuthHandler import AuthHandler
from ...daos.OrderDao import OrderDao
from ...daos.PublicDao import PublicDao
from decimal import Decimal
from ...util.checkInput import batchGetStockHqFromQuote
import time

class PublicPositionHandler(AuthHandler):
    @access.exptproc
    def get(self):
        word = self.get_argument('word','')
        status = self.get_argument('status','')
        publicdao = PublicDao()
        #获取公共券池交易底仓的所有股票
        position_list = publicdao.getPublicPositionInfo(status)
        if word != '':#过滤掉不匹配的股票
            position_list = list(filter(lambda p:p['ccode'].find(word) >= 0 or p['cname'].find(word) >= 0,position_list))

        if len(position_list) > 0:
            #######1.计算每个账户的实际可用资金############
            #去重后的所有资金账户
            uniq_acc_list = list(set([p['faccount_id'] for p in position_list]))
            uniq_ccode_list = list(set([p['ccode'] for p in position_list]))
            pos_acc_list = [] #按账户维度统计的结果集
            # 获取从上一次更新到现在的所有委托记录
            lastorderinfo = publicdao.getPublicAllLastOrderInfo()
            for acc in uniq_acc_list:
                pal = {'faccount_id' : acc}
                pal['buy_sum_normal'] = 0 #普通买入
                pal['buy_sum_margin'] = 0 #两融买入
                pal['sell_sum_normal'] = 0 #普通卖出
                pal['sell_sum_margin'] = 0 #两融卖出
                for loi in lastorderinfo:
                    loi['amount'] = loi['amount'] if loi['amount'] is not None else 0
                    loi['oamount'] = loi['oamount'] if loi['oamount'] is not None else 0
                    if int(loi['faccount_id']) == acc:#资金账户维度
                        if int(loi['side']) == 0:#买入
                            if loi['status'] in ['dealt', 'pcanceled','pexpired']:
                                if loi['otype'] == 'ptmr':#非两融
                                    pal['buy_sum_normal'] += loi['amount'] * (-1)
                                else:#两融
                                    pal['buy_sum_margin'] += loi['amount'] * (-1)
                            elif loi['status'] in ['unsend', 'tosend', 'sending', 'sent', 'pdealt', 'tocancel', 'canceling']:
                                if loi['otype'] == 'ptmr':  # 非两融
                                    pal['buy_sum_normal'] += loi['oamount'] * (-1)
                                else:  # 两融
                                    pal['buy_sum_margin'] += loi['oamount'] * (-1)
                            else:
                                pass
                        else:#卖出
                            if loi['status'] in ['dealt', 'pcanceled','pexpired']:
                                if loi['otype'] == 'ptmc':  # 非两融
                                    pal['sell_sum_normal'] += loi['amount']
                                else:  # 两融
                                    pal['sell_sum_margin'] += loi['amount']

                pos_acc_list.append(pal)

            #######2.计算已买数量 已卖数量 浮动盈亏#######
            #获取行情
            # quote_dict = batchGetStockHqFromQuote(uniq_ccode_list)

            # 获取今天所有的委托记录，用于计算头寸、买入在途金额、卖出在途金额
            todaydealtinfo = publicdao.getPublicTodayOrderInfo(self.trader_id)

            # 查表 获取当日持仓收益信息（头寸数量 头寸均价 交易盈亏）
            traderProfitInfo = publicdao.getPublicTraderProfitByDate(self.trader_id)

            # 字段计算
            for position in position_list:
                # 可开仓数
                position['open_count'] = position['acount'] - position['ocount']

                # 可用金额
                for p in pos_acc_list:
                    if p['faccount_id'] == position['faccount_id']:  # 资金账户维度
                        if position['stype'] == 1 and position['atype'] == 'margin' and position['btype'] == 'rzmr':#两融户
                            position['balance'] = position['credit'] + p['buy_sum_margin'] + p['sell_sum_margin']
                        else:#普通户
                            position['balance'] = position['balance'] + p['buy_sum_normal'] + p['sell_sum_normal']
                        break

                # 字段初始化
                position['bcount'] = 0 # 已买数量
                position['scount'] = 0 # 已卖数量
                position['buy_onroad_money'] = 0 # 买入在途金额
                position['sell_onroad_money'] = 0 # 卖出在途金额

                position['cash_count'] = 0 # 头寸数量（带方向）
                position['cash_price'] = '0.00' # 头寸成本
                position['float_profit'] = '0.00' # 浮动盈亏
                position['deal_profit'] = '0.00' # 交易盈亏

                #已买数量 已卖数量
                for tdi in todaydealtinfo:
                    tdi['dcount'] = tdi['dcount'] if tdi['dcount'] is not None else 0
                    if tdi['faccount_id'] == position['faccount_id'] and tdi['ccode'] == position['ccode']:#账户 股票两维度
                        if int(tdi['side']) == 0:
                            if tdi['status'] in ['dealt','pcanceled','pexpired']:
                                position['bcount'] += tdi['dcount']
                            elif tdi['status'] in ['unsend','tosend','sending','sent','pdealt','tocancel','canceling']:
                                position['buy_onroad_money'] += tdi['ocount1'] * tdi['oprice']
                        else:
                            if tdi['status'] in ['dealt', 'pcanceled','pexpired']:
                                position['scount'] += tdi['dcount']
                            elif tdi['status'] in ['unsend','tosend','sending','sent','pdealt','tocancel','canceling']:
                                position['sell_onroad_money'] += tdi['ocount1'] * tdi['oprice']

                position['buy_onroad_money'] = Decimal(position['buy_onroad_money']).quantize(Decimal('0.00'))
                position['sell_onroad_money'] = Decimal(position['sell_onroad_money']).quantize(Decimal('0.00'))
                # 头寸数量 头寸成本 交易盈亏 浮动盈亏
                for fp in traderProfitInfo:
                    if fp['account_id'] == position['faccount_id'] and fp['scode'] == position['ccode']:
                        position['cash_count'] = fp['count']
                        position['cash_price'] = fp['price']
                        position['deal_profit'] = fp['tprofit']
                        position['float_profit'] = Decimal(fp['count'] * (20 - float(fp['ori_price']))).quantize(Decimal('0.00'))

        data = {'list': position_list}
        self.write(protocol.success(data=data))
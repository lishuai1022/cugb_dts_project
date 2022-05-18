from ..mysql import *
from ..error import *
import json
import logging

class BScountDao(object):
    status_proccessing_list = [ #非终态
        'unsend',
        'tosend',
        'sending',
        'sent',
        'pdealt',
        'tocancel',
        'canceling'
    ]
    status_proceed_list = [ # 终态
        'canceled',
        'pcanceled',
        'dealt',
        'pexpired',
        'expired',
        'cexpired',
    ]

    def __init__(self):
        self._db = DBMysql()
        super().__init__()

    ############################可买可卖 S##################################
    # 最大可买 = max(mb1,mb2,mb3,mb4)
    # mb1:资金账户可用资金（需要用委托记录推算出“真实”的可用资金）
        # getOneSumAmount
        # getBCountWithFee2(算fee)
    # mb2:券源可买入数（读库即可）
        # 券源可买入数量 = 当前已分配数 - 买入终止态委托的已成数量汇总 - 买入中间态委托的委托数量汇总；
        # mb2 = acount - buy_succ_num - buying_num
            # acount(即oak_trader_stock表的acount字段 / 公共券池对应oak_public_stock的acount字段）
    # mb3:“买入开仓限额余额”决定的可买入数
        # 买入开仓限额余额  #买入开仓限额余额 = 买入开仓限额 - sum(abs(买入头寸股数) *头寸成本)   可能为负数
        # buy_opening_limit_left = buy_opening_limit - buy_opening_money_all
        # getBCountWithFee2(算fee)

    # mb4:"买入在途限额余额"决定的可买入数
        # 买入在途限额余额  # 买入在途限额余额 = 买入在途限额 - 买入在途金额   可能为负数
        # buy_transit_limit_left = buy_transit_limit - buying_money
        # 不算fee

    # 最大可卖 = max(ms1,ms2,ms3,ms4)
    # ms1:资金账户及时可卖数（需要用委托记录推算出“真实”的可卖出数）
        # getRealSellCount(trader_id,faccount_id,ccode)
            # getAccountPosition(faccount_id,ccode)
            # getLastOrderInfoByPosition(trader_id,faccount_id,ccode,positioninfo['mtime'],1) #所有卖出记录
    # ms2:券源可卖出数（读库即可）
        # ucount(oak_trader_stock的ucount字段 / 公共券池对应oak_public_stock的ucount字段)
    # ms3:“卖出开仓限额余额”决定的可卖出数（不算fee）
        # 卖出开仓限额余额 = 卖出开仓限额 - sum(abs(卖出头寸股数) *头寸成本)   可能为负数
        # sell_opening_limit_left = sell_opening_limit - sell_opening_money_all
    # ms4:"卖出在途限额余额"决定的可卖出数（不算fee）
        # 卖出在途限额余额  # 卖出在途限额余额 = 卖出在途限额 - 卖出在途金额   可能为负数
        # sell_transit_limit_left = sell_transit_limit - selling_money

    def _getTraderOnePosition(self, source,trader_id, faccount_id, ccode):
        '''
            获取（私有券池、交易员、资金账户、当前票）的持仓信息（1条）
        '''
        if int(source) == 0:#私有券池
            sql = """
                SELECT
                    ts.id record_id,
                    ts.trader_id,  
                    ts.ccode,
                    ts.cname,
                    ts.ucount,
                    ts.acount,
                    ap.credit as stype,
                    a.type as atype,
                    a.btype as btype,
                    ifnull(a.credit,0) credit,
                    a.balance,
                    a.status,
                    ap.ucount as apucount
                FROM oak_trader_stock ts
                LEFT JOIN oak_account_position ap ON ap.account_id=ts.account_id and ap.scode=ts.ccode
                LEFT JOIN oak_account a ON a.id=ts.account_id
                WHERE ts.trader_id='%s' and ts.account_id= '%s' and ts.ccode= '%s'
            """ % (trader_id, faccount_id, ccode)
        else: #公共券池
            sql = """
                SELECT
                    ts.id record_id,
                    ts.scode as ccode,
                    ts.sname as cname,
                    ts.ucount,
                    ts.acount,
                    ts.ocount,
                    ap.credit as stype,
                    a.type as atype,
                    a.btype as btype,
                    ifnull(a.credit,0) credit,
                    a.balance,
                    a.status,
                    ap.ucount as apucount
                FROM oak_public_stock ts
                LEFT JOIN oak_account_position ap ON ap.account_id=ts.account_id and ap.scode=ts.scode
                LEFT JOIN oak_account a ON a.id=ts.account_id
                WHERE ts.account_id= '%s' and ts.scode= '%s'
            """ % (faccount_id, ccode)
        return self._db.selectone(sql)

    def _getTodayAllOrder(self,trader_id):
        '''
            获取（公私券池、交易员、所有账户、所有票、当日）的所有交易记录
        '''
        sql = """
            SELECT 
                o.id order_id,
                o.trader_id,
                o.account_id,
                o.type, 
                o.ccode,
                o.cname,
                o.otime,
                o.dtime,
                o.side,
                o.ptype,
                o.status,
                o.oprice,
                o.ocount,
                o.ocount1,
                o.dprice,
                o.dcount,
                o.cost,
                o.costs,
                o.amount,
                o.source,
                o.ocode
            FROM oak_order o 
            WHERE o.type=0 and o.odate=date_format(now(),'%%Y-%%m-%%d') AND o.trader_id='%s'
            ORDER BY o.ctime DESC 
        """ % (trader_id)
        return self._db.selectall(sql)

    def _getNumMoney(self,source,trader_id,faccount_id,ccode):
        '''
            获取：
                买入在途金额（所有票） buying_money
                卖出在途金额（所有票） selling_money
                买入成功数量 （当前票） buy_succ_num
                买入中数量 （当前票） buying_num
                卖出成功数据量（当前票） sell_succ_num
                卖出中数据量（当前票） selling_num
        '''
        # 初始化
        buying_money = 0
        selling_money = 0
        buy_succ_num = 0
        buying_num = 0
        sell_succ_num = 0
        selling_num = 0

        # 获取（公私券池、交易员、所有账户、所有票、当日）的所有交易记录
        order_list = self._getTodayAllOrder(trader_id)
        for o in order_list:
            ocount = o['ocount1'] if o['ocount1'] is not None else 0
            dcount = o['dcount'] if o['dcount'] is not None else 0

            if o['status'] in self.status_proccessing_list:  # 进行中
                if o['side'] == 0:  # 买入
                    if int(o['source']) == int(source) and o['ccode'] == ccode and int(o['account_id']) == int(faccount_id):#只统计当前票的买入数量
                        buying_num += ocount
                    buying_money += o['ocount'] * float(o['oprice'])#所有票的买入中金额
                else:  # 卖出
                    if int(o['source']) == int(source) and o['ccode'] == ccode and int(o['account_id']) == int(faccount_id):#只统计当前票的卖出数量
                        selling_num += ocount
                    selling_money += o['ocount'] * float(o['oprice'])#所有票的卖出中金额
            elif o['status'] in self.status_proceed_list:  # 终态
                if o['side'] == 0:  # 买入
                    if int(o['source']) == int(source) and o['ccode'] == ccode and int(o['account_id']) == int(faccount_id):#只统计当前票的买入数量
                        buy_succ_num += dcount
                else:  # 卖出
                    if int(o['source']) == int(source) and o['ccode'] == ccode and int(o['account_id']) == int(faccount_id):#只统计当前票的卖出数量
                        sell_succ_num += dcount
            else:
                pass
        return {
            'buying_money':buying_money,
            'selling_money':selling_money,
            'buy_succ_num': buy_succ_num,
            'buying_num':buying_num,
            'sell_succ_num':sell_succ_num,
            'selling_num':selling_num
        }

    def _getTraderInfoById(self,trader_id):
        sql = '''
            select * from oak_trader where `delete`=0 and id='%s'
        ''' % (trader_id)
        return self._db.selectone(sql)

    def _getTraderConfiginfo(self,trader_id):
        '''
            #获取配置信息:
                买入开仓限额 buy_opening_limit
                卖出开仓限额 sell_opening_limit
                买入在途限额 buy_transit_limit
                卖出在途限额 sell_transit_limit
        '''
        # 初始化
        buy_opening_limit = 0
        sell_opening_limit = 0
        buy_transit_limit = 0
        sell_transit_limit = 0
        traderinfo = self._getTraderInfoById(trader_id)
        try:
            trader_config = json.loads(traderinfo['configs'])
            if 'opening_limit' in trader_config.keys():#买入开仓限额 卖出开仓限额
                buy_opening_limit = float(trader_config['opening_limit'])
                sell_opening_limit = float(trader_config['opening_limit'])
            if 'transit_limit' in trader_config.keys():#买入在途限额 卖出在途限额
                buy_transit_limit = float(trader_config['transit_limit'])
                sell_transit_limit = float(trader_config['transit_limit'])
        except:
            raise Exception('trader config error')

        return {
            'buy_opening_limit':buy_opening_limit,
            'sell_opening_limit':sell_opening_limit,
            'buy_transit_limit':buy_transit_limit,
            'sell_transit_limit':sell_transit_limit,
        }

    def _getTraderCash(self,trader_id):
        sql = """
            select 
                id,
                trader_id,
                account_id,
                scode,
                sname,
                count,
                ifnull(price,0) ori_price,
                round(ifnull(price,0),2) price,
                source,
                round(ifnull(profit,0),2) profit 
            from oak_trader_profit where trader_id='%s'
        """ % trader_id

        return self._db.selectall(sql)
    def _getMoneyLimit(self,source,trader_id,faccount_id,ccode,config_money_limit_info,num_money_info):
        buy_opening_limit = config_money_limit_info['buy_opening_limit']
        sell_opening_limit = config_money_limit_info['sell_opening_limit']
        buy_transit_limit = config_money_limit_info['buy_transit_limit']
        sell_transit_limit = config_money_limit_info['sell_transit_limit']
        buy_opening_money = 0
        sell_opening_money = 0
        buy_opening_money_all = 0
        sell_opening_money_all = 0
        buying_money = num_money_info['buying_money']
        selling_money = num_money_info['selling_money']
        cash_count = 0
        cash_price = 0

        # 获取该交易员"所有票"的头寸信息
        cashinfoall = self._getTraderCash(trader_id)
        if len(cashinfoall) > 0:
            for cia in cashinfoall:
                if int(cia['source']) == int(source) and cia['scode'] == ccode and int(cia['account_id']) == int(faccount_id):
                    cash_count = cia['count']
                    cash_price = float(cia['ori_price'])
                    if cia['count'] > 0:
                        buy_opening_money += abs(float(cia['ori_price']) * cia['count'])  # 股票买入开仓金额（该股票）
                    else:
                        sell_opening_money += abs(float(cia['ori_price']) * cia['count'])  # 股票卖出开仓金额（该股票）

                if cia['count'] > 0:
                    buy_opening_money_all += abs(float(cia['ori_price']) * cia['count'])  # 股票买入开仓金额（所有票）
                else:
                    sell_opening_money_all += abs(float(cia['ori_price']) * cia['count'])  # 股票买入开仓金额（所有票）

        # 买入开仓限额余额  #买入开仓限额余额 = 买入开仓限额 - sum(abs(买入头寸股数) *头寸成本)   可能为负数
        buy_opening_limit_left = buy_opening_limit - buy_opening_money_all
        # 卖出开仓限额余额  #卖出开仓限额余额 = 卖出开仓限额 - sum(abs(卖出头寸股数) *头寸成本)   可能为负数
        sell_opening_limit_left = sell_opening_limit - sell_opening_money_all
        # 买入在途限额余额  # 买入在途限额余额 = 买入在途限额 - 买入在途金额   可能为负数
        buy_transit_limit_left = buy_transit_limit - buying_money
        # 卖出在途限额余额  # 卖出在途限额余额 = 卖出在途限额 - 卖出在途金额   可能为负数
        sell_transit_limit_left = sell_transit_limit - selling_money

        return {
            'buy_opening_limit_left':buy_opening_limit_left,
            'sell_opening_limit_left':sell_opening_limit_left,
            'buy_transit_limit_left':buy_transit_limit_left,
            'sell_transit_limit_left':sell_transit_limit_left,
            'cash_count':cash_count,
            'cash_price':cash_price,
        }

    def _getAccountSumAmount(self,faccount_id):
        pal = {
            'buy_sum_normal': 0,  # 普通买入
            'buy_sum_margin': 0,  # 两融买入
            'sell_sum_normal': 0,  # 普通卖出
            'sell_sum_margin': 0  # 两融卖出
        }
        sql = """
            SELECT 
                o.account_id faccount_id,
                o.side,
                o.amount,
                o.oamount,
                o.`status`,
                o.`otype` as otype
            from `oak_order` o 
            left join oak_account as ac on o.account_id=ac.id
            where o.odate=curdate() and o.ctime>=ac.mtime and o.account_id='%s'
        """ % (faccount_id)
        lastorderinfo = self._db.selectall(sql)

        if len(lastorderinfo) > 0:
            for loi in lastorderinfo:
                loi['amount'] = loi['amount'] if loi['amount'] is not None else 0
                loi['oamount'] = loi['oamount'] if loi['oamount'] is not None else 0
                if int(loi['side']) == 0:  # 买入
                    if loi['status'] in ['dealt', 'pcanceled', 'pexpired']:
                        if loi['otype'] == 'ptmr':  # 非两融
                            pal['buy_sum_normal'] += loi['amount'] * (-1)
                        else:  # 两融
                            pal['buy_sum_margin'] += loi['amount'] * (-1)
                    elif loi['status'] in ['unsend', 'tosend', 'sending', 'sent', 'pdealt', 'tocancel',
                                           'canceling']:
                        if loi['otype'] == 'ptmr':  # 非两融
                            pal['buy_sum_normal'] += loi['oamount'] * (-1)
                        else:  # 两融
                            pal['buy_sum_margin'] += loi['oamount'] * (-1)
                    else:
                        pass
                else:  # 卖出
                    if loi['status'] in ['dealt', 'pcanceled', 'pexpired']:
                        if loi['otype'] == 'ptmc':  # 非两融
                            pal['sell_sum_normal'] += loi['amount']
                        else:  # 两融
                            pal['sell_sum_margin'] += loi['amount']

        return pal

    def _floor100(self,number):
        return int(float(number) / 100) * 100

    def _get_sum_fee(self,oprice,temp_count,buy_rate_config_list):
        real_sum_fee = 0  # 真实的总费用
        cash_without_fee = oprice * temp_count
        for item in buy_rate_config_list:
            item_fee = cash_without_fee * float(item['value'])
            if item['max'] is not None and item['max'] != '' and item['max'] != 'null' and item_fee > float(item['max']):
                real_sum_fee += float(item['max'])
            elif item['min'] is not None and item['min'] != '' and item['min'] != 'null' and item_fee < float(item['min']):
                real_sum_fee += float(item['min'])
            else:
                real_sum_fee += item_fee
        return real_sum_fee

    def _getBCountWithFee(self,cash,oprice,buy_rate_config_list):
        sum_rate = sum([float(item['value']) for item in buy_rate_config_list]) #总费率
        temp_count = self._floor100(cash/(oprice * (1+sum_rate)))#第一次的最大可买数
        temp_cash = oprice * temp_count + self._get_sum_fee(oprice,temp_count,buy_rate_config_list)#第一次计算所需钱数

        while temp_cash < cash:#少了，尝试 +100
            temp_count += 100
            temp_cash = oprice * temp_count + self._get_sum_fee(oprice,temp_count,buy_rate_config_list)

        while temp_cash > cash:#多了，尝试 -100
            temp_count -= 100
            temp_cash = oprice * temp_count + self._get_sum_fee(oprice,temp_count,buy_rate_config_list)

        return temp_count

    def _getBuyRateConfig(self,faccount_id,ccode):
        ##获取费率
        sql = """
            SELECT 
                *
            FROM oak_account
            WHERE id='%s'
        """ % (faccount_id)
        account_info = self._db.selectone(sql)
        try:
            account_config = json.loads(account_info['configs'])
            if 'cost' in account_config:
                cost_config = account_config['cost']
            else:  # 账户没配置，用系统配置
                sql = """
                    select value from oak_configure where code='cost'
                """
                res = self._db.selectone(sql)
                if res is None:
                    raise ValueError
                cost_config = json.loads(res['value'])
            if ccode[0] == '6':  # sh
                ex = 'sh'
            else:  # sz
                ex = 'sz'
            buy_rate_config_list = cost_config['buy'][ex]
        except:
            raise Exception('account data error')
        return buy_rate_config_list

    # 获取资金账户的即时可卖数
    def _getRealSellCount(self, faccount_id, ccode,ori_ucount):
        sql1 = """
            SELECT 
                ifnull(sum(ocount1),0) sum_ocount1
            FROM `oak_order` o 
            LEFT JOIN oak_account_position as ap on (o.account_id=ap.account_id and o.ccode=ap.scode)
            WHERE o.ctime>=ap.mtime and o.account_id='%s' and ccode='%s' and o.side=1
        """ % (faccount_id,ccode)
        res1 = self._db.selectall(sql1)
        all_order_count = 0
        if res1 is not None:
            all_order_count = res1[0]['sum_ocount1']

        sql2 = """
            SELECT 
                IFNULL(sum(ocount1),0) sum_ocount1,
                IFNULL(sum(dcount1),0) sum_dcount1
            FROM `oak_order` o 
            LEFT JOIN oak_account_position as ap on (o.account_id=ap.account_id and o.ccode=ap.scode)
            WHERE o.mtime>=ap.mtime and o.account_id='%s' and ccode='%s' and o.side=1
            and status in ('dealt', 'pcanceled', 'pexpired', 'canceled', 'expired')
        """ % (faccount_id,ccode)
        res2 = self._db.selectall(sql2)
        all_gap_count = 0
        if res2 is not None:
            all_gap_count = res2[0]['sum_ocount1'] - res2[0]['sum_dcount1']

        import logging
        logging.info('ori_ucount=%s,all_order_count=%s,all_gap_count=%s' % (ori_ucount,all_order_count,all_gap_count))

        real_count = max(0, ori_ucount - all_order_count + all_gap_count)
        return real_count

    # 获取当日 公共券池 该交易员 该户 该票的所有交易记录
    def _getTodayMyPubCodeOrders(self,trader_id,faccount_id,ccode,source=1):
        sql = """
            select 
                * 
            from oak_order 
            where `odate`=CURDATE() and source='%s' and trader_id='%s' and account_id='%s' and ccode='%s'
        """ % (source,trader_id,faccount_id,ccode)
        return self._db.selectall(sql)

    def _getMyPubCountSum(self,trader_id,faccount_id,ccode,source=1):
        pub_buying_num = 0
        pub_selling_num = 0
        pub_buy_succ_num = 0
        pub_sell_succ_num = 0

        order_list = self._getTodayMyPubCodeOrders(trader_id,faccount_id,ccode,source)
        if len(order_list) > 0:
            for o in order_list:
                ocount = o['ocount1'] if o['ocount1'] is not None else 0
                dcount = o['dcount'] if o['dcount'] is not None else 0

                if o['status'] in self.status_proccessing_list:  # 进行中
                    if o['side'] == 0:  # 买入
                        pub_buying_num += ocount
                    else:  # 卖出
                        pub_selling_num += ocount
                elif o['status'] in self.status_proceed_list:  # 终态
                    if o['side'] == 0:  # 买入
                        pub_buy_succ_num += dcount
                    else:  # 卖出
                        pub_sell_succ_num += dcount
                else:
                    pass

        return {
            'pub_buying_num':pub_buying_num,
            'pub_selling_num':pub_selling_num,
            'pub_buy_succ_num':pub_buy_succ_num,
            'pub_sell_succ_num':pub_sell_succ_num
        }

    def _getMyPubRecentOneCash(self,trader_id,faccount_id,ccode,source):
        sql = """
            SELECT
                * 
            FROM
                oak_trader_profit_record 
            WHERE
                trader_id = '%s' 
                AND account_id = '%s' 
                AND scode = '%s' 
                AND source = '%s' 
                AND date <= CURDATE( ) 
            ORDER BY
                date DESC 
                LIMIT 1
        """ % (trader_id,faccount_id,ccode,source)
        return self._db.selectone(sql)

    def getBscount(self,source,trader_id,faccount_id,ccode,price):
        price = float(price)
        position_info = self._getTraderOnePosition(source,trader_id, faccount_id, ccode)
        if position_info is None:
            raise trd_no_position_error
        stype = position_info['stype'] #是否两融标的
        btype = position_info['btype'] #买入方式
        acount = position_info['acount'] #分配数量
        atype = position_info['atype'] #账户类型 两融或普通
        ucount = position_info['ucount'] #可卖数量

        buy_rate_config_list = self._getBuyRateConfig(faccount_id, ccode)
        num_money_info = self._getNumMoney(source,trader_id,faccount_id,ccode)
        config_money_limit_info = self._getTraderConfiginfo(trader_id)
        money_left_info = self._getMoneyLimit(source,trader_id,faccount_id,ccode,config_money_limit_info,num_money_info)
        cash_count = money_left_info['cash_count']
        cash_price = money_left_info['cash_price']
        buy_opening_limit_left = money_left_info['buy_opening_limit_left']
        buy_transit_limit_left = money_left_info['buy_transit_limit_left']
        sell_opening_limit_left = money_left_info['sell_opening_limit_left']
        sell_transit_limit_left = money_left_info['sell_transit_limit_left']

        pub_count_sum = self._getMyPubCountSum(trader_id,faccount_id,ccode,source)
        pub_buying_num = pub_count_sum['pub_buying_num']
        pub_selling_num = pub_count_sum['pub_selling_num']
        pub_buy_succ_num = pub_count_sum['pub_buy_succ_num']
        pub_sell_succ_num = pub_count_sum['pub_sell_succ_num']

        # 获取该交易员 该户 该票 公共券池的累计隔夜头寸
        pubCashCount = 0
        if int(source) == 1:
            pubRecentOneCash = self._getMyPubRecentOneCash(trader_id, faccount_id, ccode, source)
            if pubRecentOneCash is not None:
                pubCashCount = pubRecentOneCash['count']

        logging.info('--------------bscount B---------------------')
        ################## 最大可买数量 ################
        # mb1资金户可用资金 决定的最大可买
        suminfo = self._getAccountSumAmount(faccount_id)
        if stype == 1 and atype == 'margin' and btype == 'rzmr':  # 两融
            m1 = float(position_info['credit']) + float(suminfo['buy_sum_margin']) + float(suminfo['sell_sum_margin'])
            logging.info('credit=%s,buy_sum_margin=%s,sell_sum_margin=%s' % (position_info['credit'],suminfo['buy_sum_margin'],suminfo['sell_sum_margin']))
        else:  # 非两融
            m1 = float(position_info['balance']) + float(suminfo['buy_sum_normal']) + float(suminfo['sell_sum_normal'])
            logging.info('balance=%s,buy_sum_normal=%s,sell_sum_normal=%s' % (position_info['balance'],suminfo['buy_sum_normal'],suminfo['sell_sum_normal']))
        mb1 = self._getBCountWithFee(m1, price, buy_rate_config_list)

        # mb2 券源可买入数量
        if int(source) == 0: #私有券池
            # 券源可买入数量 = 当前已分配数 - 买入终止态委托的已成数量汇总 - 买入中间态委托的委托数量汇总；
            mb2 = acount - num_money_info['buy_succ_num'] - num_money_info['buying_num']
            logging.info('acount=%s, buy_succ_num=%s,buying_num=%s' % (acount,num_money_info['buy_succ_num'],num_money_info['buying_num']))
        else: # 公共券池
            # 券源的即时可买数 = 公共券池已分数 - 公共券池占用数 - 该交易员隔夜头寸数（多头为正数，空头为负数）- Min【0，（该交易员买入终止态委托的已成数量汇总 + 该交易员买入中间态委托的委托数量汇总）-（该交易员卖出终止态委托的已成数量汇总 + 该交易员卖出中间态委托的委托数量汇总）】
            mb2 = position_info['acount'] - position_info['ocount'] - min(0,(pub_buy_succ_num + pub_buying_num) - (pub_sell_succ_num + pub_selling_num) + pubCashCount)
            logging.info('acount=%s,ocount%s,pub_buy_succ_num=%s,pub_buying_num=%s,pub_sell_succ_num=%s,pub_selling_num=%s,pubCashCount=%s' % (position_info['acount'],position_info['ocount'],pub_buy_succ_num,pub_buying_num,pub_sell_succ_num,pub_selling_num,pubCashCount))

        # mb3 买入开仓限额余额 决定的最大可买
        if cash_count >= 0:
            if position_info['status'] == 'normal': #正常
                m3 = max(0, buy_opening_limit_left)
                mb3 = self._getBCountWithFee(m3, price, buy_rate_config_list)
            else: #锁买卖 禁开仓 和 其他
                mb3 = 0
        else:
            if position_info['status'] == 'normal':  # 正常
                m3 = max(0, buy_opening_limit_left) + abs(cash_count * cash_price)
                mb3 = self._getBCountWithFee(m3, price, buy_rate_config_list)
            elif position_info['status'] == 'olimit':  # 禁开仓
                mb3 = self._floor100(abs(cash_count))
            else: #锁买卖 和 其他
                mb3 = 0

        # mb4 买入在途限额余额 决定的最大可买
        m4 = max(0, buy_transit_limit_left)
        mb4 = max(0, self._floor100(m4 / price))

        # 最大可买数量
        mbcount = max(0, self._floor100(min(mb1,mb2, mb3, mb4)))

        ################## 最大可卖出数量 ################
        # ms1 券源可卖数
        if int(source) == 0:  # 私有券池
            ms1 = ucount
        else: # 公共券池
            # 即时可买数 = 公共券池已分数 - 公共券池占用数 + 该交易员隔夜头寸数（多头为正数，空头为负数）- Min【0，（该交易员卖出终止态委托的已成数量汇总 + 该交易员卖出中间态委托的委托数量汇总）-（该交易员买入终止态委托的已成数量汇总 + 该交易员买入中间态委托的委托数量汇总）】
            ms1 = position_info['acount'] - position_info['ocount'] - min(0, (pub_sell_succ_num + pub_selling_num) - (pub_buy_succ_num + pub_buying_num) - pubCashCount)
            logging.info('position_info_acount=%s, position_info_ocount=%s' % (position_info['acount'] ,position_info['ocount']))
            logging.info('pub_sell_succ_num=%s,pub_selling_num=%s,pub_buy_succ_num=%s, pub_buying_num=%s ,pubCashCount=%s' % (pub_sell_succ_num, pub_selling_num,pub_buy_succ_num,pub_buying_num,pubCashCount))

        # ms2 卖出开仓限额余额可卖
        if cash_count <= 0:
            if position_info['status'] == 'normal': #正常
                ms2 = self._floor100(max(0, sell_opening_limit_left) / price)
            else:  # 锁买卖 禁开仓 和 其他
                ms2 = 0
        else:
            if position_info['status'] == 'normal':  # 正常
                ms2 = self._floor100((max(0, sell_opening_limit_left) + abs(cash_count * cash_price)) / price)
            elif position_info['status'] == 'olimit':  # 禁开仓
                ms2 = self._floor100(abs(cash_count))
            else: #锁买卖 和 其他
                ms2 = 0


        ###卖出在途限额余额可卖
        ms3 = max(0, self._floor100(sell_transit_limit_left / price))

        ###资金户即时可卖数
        ms4 = self._getRealSellCount(faccount_id, ccode,position_info['apucount'])

        # 最大可卖
        mscount = max(0, min(ms1, ms2, ms3, ms4))


        logging.info('buy_transit_limit_left=%s,sell_transit_limit_left=%s' % (buy_transit_limit_left,sell_transit_limit_left))
        logging.info('buy_opening_limit_left=%s,sell_opening_limit_left=%s' % (buy_opening_limit_left,sell_opening_limit_left))
        logging.info('apucount=%s' % position_info['apucount'])
        logging.info('ms1=%s, ms2=%s, ms3=%s, ms4=%s' % (ms1, ms2, ms3, ms4))
        logging.info('mb1=%s, mb2=%s, mb3=%s, mb4=%s' % (mb1, mb2, mb3, mb4))
        logging.info('--------------bscount E---------------------')

        data = {
            'mbcount': mbcount,
            'mscount': mscount
        }
        return data
    ############################可买可卖 E##################################

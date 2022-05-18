from ..mysql import *
from .ConfigureDao import ConfigureDao
from ..util import checkInput
import time,math,json
from .TraderDao import TraderDao
from ..util.miscUtil import *
from ..daos.PerformDao import PerformDao

class OrderDao(object):
    def __init__(self):
        self._db = DBMysql()
        super().__init__()

    def getTraderPosition(self,trader_id):
        '''
            获取交易底仓
        '''
        sql = """
        	SELECT
        		ts.id record_id,
        		ts.trader_id,  
        		ts.ccode,
        		ts.cname,
        		a.id faccount_id,
        		a.alias fname,
        		ts.acount
        	FROM oak_trader_stock ts
        	LEFT JOIN oak_account a ON ts.account_id=a.id
        	WHERE ts.trader_id='%s'
        	ORDER BY ts.ccode,ts.id ASC
        """ % (trader_id)
        return self._db.selectall(sql)

    def getTraderOnePosition(self,trader_id,faccount_id,ccode):
        '''
            获取交易底仓
        '''
        sql = """
        	SELECT
        		ts.id record_id,
        		ts.trader_id,  
        		ts.ccode,
        		ts.cname,
        		ts.ucount,
        		ap.credit as stype,
        		a.type as atype,
        		a.btype as btype,
        		ifnull(a.credit,0) credit,
        		a.balance
        	FROM oak_trader_stock ts
        	LEFT JOIN oak_account_position ap ON ap.account_id=ts.account_id and ap.scode=ts.ccode
        	LEFT JOIN oak_account a ON a.id=ts.account_id
        	WHERE ts.trader_id='%s' and ts.account_id= '%s' and ts.ccode= '%s'
        """ % (trader_id,faccount_id,ccode)
        return self._db.selectone(sql)

    def getTraderDailyStatInfo(self,trader_id,isVirtual=False):
        '''
            获取交易员当天的统计信息 买入数量 卖出数量 成交金额等
        :param trader_id:
        :return:
        '''
        configDao = ConfigureDao()
        # holidays = configDao.getHolidays()
        # stimestamp = checkInput.getTodayStartTimestamp(holidays)  # 开始毫秒时间戳
        import datetime
        today = datetime.date.today()
        stimestamp = int(time.mktime(today.timetuple())) * 1000

        vitural_sql = ''
        if isVirtual == False:  # 不包含虚拟记录，只取真实记录
            vitural_sql = " AND o.type=0"

        sql = """
            SELECT 
                record_id,
                trader_id,
                account_id,
                ccode,
                side,
                sum(o.dcount) sum_count,
                sum(o.amount) sum_amount from `oak_order` o
            WHERE `trader_id`='%s' and o.`status` in ('dealt','pcanceled') and o.ctime>='%s' %s
            GROUP BY o.account_id,ccode,o.side
        """ % (trader_id,stimestamp,vitural_sql)
        # print(sql)
        return self._db.selectall(sql)


    def getTraderDailyOrder(self,trader_id,item='',isVirtual=False,record_id='',stimestamp=''):
        '''
            获取交易员"当天"的委托记录
        :param trader_id:交易员id
        :param item:筛选类型 默认为空表示全部 dealt-已成交 canceled-已撤订单 多选时用英文逗号连接
        :param isVirtual:是否包含虚拟记录
        :return:委托记录list
        '''
        configDao = ConfigureDao()
        holidays = configDao.getHolidays()
        if stimestamp == '':
            stimestamp = checkInput.getTodayStartTimestamp(holidays)  # 开始毫秒时间戳

        condition_sql = ''
        if item == 'can_cancel':#可撤单
            condition_sql = " AND status IN ('unsend','tosend','sending','sent','pdealt') "
        elif item == 'dealt':#已成交
            condition_sql = " AND status IN ('dealt') "
        elif item == 'canceled':#已撤单
            condition_sql = " AND status IN ('canceled') "
        elif item == 'canceled,dealt' or item == 'dealt,canceled':#已成交 #已撤单
            condition_sql = " AND status IN ('canceled','dealt') "
        elif item == 'can_cancel,dealt' or item == 'dealt,can_cancel':#已成交 #可撤单
            condition_sql = " AND status IN ('dealt','unsend','tosend','sending','sent','pdealt') "
        elif item == 'canceled,can_cancel' or item == 'dealt,can_cancel':#可撤单 #已撤单
            condition_sql = " AND status IN ('canceled','unsend','tosend','sending','sent','pdealt') "
        else:#全部
            pass

        vitural_sql = ''
        if isVirtual == False:#不包含虚拟记录，只取真实记录
            vitural_sql = " AND o.type=0"

        record_sql = ''
        if record_id != '':
            record_sql = " AND o.record_id='%s' " % (record_id)


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
                o.ocode
        	FROM oak_order o 
	        WHERE o.ctime>='%s' AND o.trader_id='%s' %s %s %s
	        ORDER BY o.ctime DESC 
        """ % (stimestamp,trader_id,condition_sql,vitural_sql,record_sql)
        # print(sql)

        return self._db.selectall(sql)

    def getTraderDailyOrder2(self, trader_id, item=''):
            '''
                获取交易员"当天"的委托记录
            :param trader_id:交易员id
            :param item:筛选类型 默认为空表示全部 dealt-已成交 canceled-已撤订单 多选时用英文逗号连接
            :param isVirtual:是否包含虚拟记录
            :return:委托记录list
            '''
            configDao = ConfigureDao()
            holidays = configDao.getHolidays()
            stimestamp = checkInput.getTodayStartTimestamp(holidays)  # 开始毫秒时间戳

            condition_sql = ''
            if item == 'can_cancel':  # 可撤单
                condition_sql = " AND o.status IN ('unsend','tosend','sending','sent','pdealt') "
            elif item == 'dealt':  # 已成交
                condition_sql = " AND o.status IN ('dealt') "
            elif item == 'canceled':  # 已撤单
                condition_sql = " AND o.status IN ('canceled') "
            elif item == 'canceled,dealt' or item == 'dealt,canceled':  # 已成交 #已撤单
                condition_sql = " AND o.status IN ('canceled','dealt') "
            elif item == 'can_cancel,dealt' or item == 'dealt,can_cancel':  # 已成交 #可撤单
                condition_sql = " AND o.status IN ('dealt','unsend','tosend','sending','sent','pdealt') "
            elif item == 'canceled,can_cancel' or item == 'dealt,can_cancel':  # 可撤单 #已撤单
                condition_sql = " AND o.status IN ('canceled','unsend','tosend','sending','sent','pdealt') "
            else:  # 全部
                pass

            # vitural_sql = " AND o.type=0"
            vitural_sql = ""

            sql = """
            	SELECT 
            		o.id order_id,
                    o.trader_id,
                    o.account_id,
                    o.record_id,
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
                    o.dprice,
                    o.dcount,
                    o.stax,
                    o.tfee,
                    o.rfee,
                    o.mfee,
                    o.amount,
                    o.ocode,
                    a.id faccount_id,
                    a.`alias` fname
            	FROM oak_order o 
            	LEFT JOIN oak_account a ON o.account_id=a.id
    	        WHERE o.ctime>='%s' AND o.trader_id='%s' %s %s
    	        ORDER BY o.ctime DESC 
            """ % (stimestamp, trader_id, condition_sql, vitural_sql)

            return self._db.selectall(sql)

    def getTraderProfitListTotal(self,trader_id,faccount_id='',ccode='',sdate='',edate='',source='0'):
        '''
            获取盈亏报表记录数量
        '''
        where_sql = " WHERE pr.trader_id = '%s' " % (str(trader_id))
        if ccode != '':
            where_sql += " AND pr.scode='%s' " % (ccode)

        if faccount_id != '':
            where_sql += " AND pr.account_id in (%s) " % (str(faccount_id))

        if sdate != '' and edate != '':
            where_sql += " AND pr.date>='%s' AND pr.date<='%s' " % (sdate, edate)

        if source == '0': #私有券池
            where_sql += ' AND pr.`source`=0 '
        elif source == '1': #公共券池
            where_sql += ' AND pr.`source`=1 '
        else: #全部
            pass

        sql = """
            SELECT count(*) total,round(ifnull(sum(ifnull(profit,0)),0),2) as sum_profit FROM oak_trader_profit_record as pr %s
        """ % (where_sql)
        # print(sql)
        res = self._db.selectone(sql)
        return res

    def getTraderProfitList(self,trader_id,faccount_id='',ccode='',sdate='',edate='',page=1,pagesize=10,pflag=True,source='0',sort='',order=''):
        '''
            获取盈亏报表
        '''
        where_sql = " WHERE pr.trader_id = '%s' " % (str(trader_id))
        if ccode != '':
            where_sql += " AND pr.scode='%s' " % (ccode)

        if faccount_id != '':
            where_sql += " AND pr.account_id in (%s) " % (str(faccount_id))

        if sdate != '' and edate != '':
            where_sql += " AND pr.date>='%s' AND pr.date<='%s' " % (sdate, edate)

        if source == '0': #私有券池
            where_sql += ' AND pr.`source`=0 '
        elif source == '1': #公共券池
            where_sql += ' AND pr.`source`=1 '
        else: #全部
            pass
        sort_sql = ''
        if sort != '' and order != '':
            map_dict = {
                'odate': 'pr.date',
                'ccode': 'pr.scode',
                'cname': 'pr.sname',
                'fname': 'a.alias',
                'tprofit': 'pr.tprofit',
                'interest': 'pr.interest',
                'profit': 'pr.profit',
                'source': 'pr.source',
            }
            if sort in map_dict.keys():
                sort = map_dict[sort]
            else:
                sort = 'pr.date'
            sort_sql = ' ORDER BY %s %s ' % (sort,order)

        limit_sql = ''
        if page!=0 and pagesize!='' and pflag==True:
            offset = (int(page)-1) * int(pagesize)
            limit_sql = ' LIMIT %s,%s ' % (offset,pagesize)
        sql = """
            SELECT
                pr.date as odate,
                pr.account_id as faccount_id,
                pr.scode as ccode,
                pr.sname as cname,
                a.alias as fname,
                round(ifnull(pr.tprofit,0.0000),2) as tprofit,
                round(ifnull(pr.interest,0.0000),2) as interest,
                round(ifnull(pr.profit,0.0000),2) as profit,
                pr.`source`
            FROM oak_trader_profit_record pr
            LEFT JOIN oak_account a ON pr.account_id=a.id
            %s
            %s
            %s
        """ % (where_sql,sort_sql,limit_sql)
        # print(sql)
        return self._db.selectall(sql)

    def getAccountList(self,record_id_str):
        sql = """
            SELECT
                ts.id record_id,
                a.id faccount_id,
                a.`alias` fname
            FROM oak_trader_stock ts
            LEFT JOIN oak_account a ON ts.account_id=a.id
            WHERE ts.id in (%s) 
        """ % (record_id_str)
        return self._db.selectall(sql)

    def getAllOrderListTotal(self,trader_id,faccount_id='',ccode='',side='',sdate='',edate='',source='0'):
        '''
            获取委托记录数，按条件筛选，不包含虚拟记录
        '''

        condition_sql = ''
        if faccount_id != '':
            condition_sql += ' AND a.id in (%s) ' % (faccount_id)
        if ccode != '':
            condition_sql += ' AND o.ccode="%s" ' % (ccode)
        if side != '':
            condition_sql += ' AND o.side="%s" ' % (side)
        if sdate != '' and edate != '':
            condition_sql += ' AND o.odate>="%s" AND o.odate<="%s" ' % (sdate,edate)
        if source == '0': #私有券池
            condition_sql += ' AND o.`source`=0 '
        elif source == '1': #公共券池
            condition_sql += ' AND o.`source`=1 '
        else: #全部
            pass

        sql = """
                	SELECT 
                		count(*) total
                	FROM oak_order o 
                    LEFT JOIN oak_account a ON o.account_id=a.id
        	        WHERE o.trader_id='%s' %s 
                """ % (trader_id, condition_sql)

        # print(sql)
        res = self._db.selectone(sql)
        return res['total']

    def getAllOrderList(self,trader_id,faccount_id='',ccode='',side='',sdate='',edate='',page=1,pagesize=10,pflag=True,source='0',sort='',order=''):
        '''
            获取委托记录，按条件筛选，包含虚拟记录
        '''

        limit_sql = ''
        if page!='' and pagesize!='' and pflag == True:
            offset = (int(page)-1) * int(pagesize)
            limit_sql = ' LIMIT %s,%s ' % (offset,pagesize)

        condition_sql = ''
        if faccount_id != '':
            condition_sql += ' AND a.id in (%s) ' % (faccount_id)
        if ccode != '':
            condition_sql += ' AND o.ccode="%s" ' % (ccode)
        if side != '':
            condition_sql += ' AND o.side="%s" ' % (side)
        if sdate != '' and edate != '':
            condition_sql += ' AND o.odate>="%s" AND o.odate<="%s" ' % (sdate,edate)
        if source == '0': #私有券池
            condition_sql += ' AND o.`source`=0 '
        elif source == '1': #公共券池
            condition_sql += ' AND o.`source`=1 '
        else: #全部
            pass

        sort_sql = ''
        if sort != '' and order != '':
            map_dict = {
                "order_id": "o.id",
                "ccode": "o.ccode",
                "cname": "o.cname",
                "fname": "a.alias",
                "source": "o.`source`",
                "ocode": "o.ocode",
                "side": "o.side",
                "status": "o.status",
                "otype": "o.otype",
                "oprice": "o.oprice",
                "ocount": "o.ocount",
                "dprice": "o.dprice",
                "dcount": "o.dcount",
                "dmoney": "o.dprice*o.dcount",
                "cost": "o.`cost`",
                "amount": "o.amount",
                "otime": "o.otime",
                "dtime": "o.dtime",
                "type": "o.`type`",
            }
            if sort in map_dict.keys():
                sort = map_dict[sort]
            else:
                sort = 'o.id'
            sort_sql = ' ORDER BY %s %s ' % (sort, order)

        sql = """
                	SELECT 
                		o.id order_id,
                        o.trader_id,
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
                        o.dprice,
                        o.dcount,
                        o.cost,
                        o.costs,
                        o.amount,
                        o.ocode,
                        o.otype,
                        o.`source`,
                        a.id faccount_id,
                        a.alias fname,
                        o.odate
                	FROM oak_order o 
                    LEFT JOIN oak_account a ON o.account_id=a.id
        	        WHERE o.trader_id='%s' %s 
        	        %s
        	        %s
                """ % (trader_id, condition_sql,sort_sql,limit_sql)

        # print(sql)
        return self._db.selectall(sql)

    def getAllFillListTotal(self,trader_id,faccount_id='',ccode='',side='',stimestamp='',etimestamp=''):
        '''
            获取成交记录数，按条件筛选，不包含虚拟记录
        '''

        condition_sql = ''
        if faccount_id != '':
            condition_sql += ' AND oor.account_id in (%s) ' % (faccount_id)
        if ccode != '':
            condition_sql += ' AND oor.ccode="%s" ' % (ccode)
        if side != '':
            condition_sql += ' AND oor.side="%s" ' % (side)
        if stimestamp != '' and stimestamp != '':
            condition_sql += ' AND oor.ctime>="%s" AND oor.ctime<="%s" ' % (stimestamp, etimestamp)

        sql = """
                	SELECT 
                		count(*) total
                	FROM oak_order oor
        	        WHERE oor.dcount>0 and oor.trader_id='%s' %s 
                """ % (trader_id, condition_sql)

        # print(sql)
        res = self._db.selectone(sql)
        return res['total']

    def getAllFillList(self,trader_id,faccount_id='',ccode='',side='',stimestamp='',etimestamp='',page=1,pagesize=10,pflag=True):
        '''
            获取成交记录，按条件筛选，包含虚拟记录
        '''

        limit_sql = ''
        if page!='' and pagesize!='' and pflag == True:
            offset = (int(page)-1) * int(pagesize)
            limit_sql = ' LIMIT %s,%s ' % (offset,pagesize)

        condition_sql = ''
        if faccount_id != '':
            condition_sql += ' AND oor.account_id in (%s) ' % (faccount_id)
        if ccode != '':
            condition_sql += ' AND oor.ccode="%s" ' % (ccode)
        if side != '':
            condition_sql += ' AND oor.side="%s" ' % (side)
        if stimestamp != '' and stimestamp != '':
            condition_sql += ' AND oor.ctime>="%s" AND oor.ctime<="%s" ' % (stimestamp,etimestamp)

        sql = """
                	SELECT  
                        oor.id order_id,
                        oor.trader_id,
                        oor.ccode,
                        oor.cname,
                        oor.account_id faccount_id,
                        a.alias fname,
                        oor.dtime,
                        oor.side,
                        oor.dprice,
                        oor.dcount,
                        oor.amount,
                        oor.ocode
                	FROM oak_order oor
                    LEFT JOIN oak_account a ON oor.account_id=a.id
        	        WHERE oor.dcount>0 and oor.trader_id='%s' %s 
        	        ORDER BY oor.ctime DESC
        	        %s
                """ % (trader_id, condition_sql,limit_sql)

        # print(sql)
        return self._db.selectall(sql)

    def getFaccountList(self,trader_id):
        sql = """
            select res.account_id as faccount_id,ifnull(a.alias,'') as fname 
            from (select account_id from oak_order where trader_id='%s' and account_id is not null group by account_id) as res
            left join `oak_account` a on a.id=res.`account_id`
        """ % (trader_id)
        return self._db.selectall(sql)

    def getConfiginfo(self,list1=[]):
        '''获取配置信息'''
        sql = """
            SELECT 
                code,
                `value`
            FROM oak_configure
        """

        res = self._db.selectall(sql)

        ret = {}
        for v in res:
            code = v.get('code')
            value = v.get('value')
            if code in list1:
                ret[code] = value
        return ret


    def searchStock(self,trader_id,keyword='',faccount_id=''):
        '''
            股票搜索
        '''

        if keyword == '':
            return []

        #请求外部接口，获取股票集合
        all_stock_list = getAllStocks()
        stock_code_res = []
        for s in all_stock_list:
            if keyword in s['code'] or keyword in s['pinyin1'] or keyword in s['name']:
                stock_code_res.append(s['code'])

        #找出所有底仓股票
        where = ' WHERE trader_id="%s" ' % (trader_id)
        if faccount_id != '':
            where += ' AND a.id="%s" ' % (faccount_id)
        sql = """
              SELECT 
                ts.id,
                ts.ccode, 
                ts.`cname`, 
                a.id faccount_id,
                a.alias fname
              FROM oak_trader_stock ts
              LEFT JOIN oak_account a ON ts.account_id=a.id 
              %s
              LIMIT 20
            """ % (where)
        # print(sql)
        res = self._db.selectall(sql)

        #求交集
        res_list = []
        for r in res:
            if r['ccode'] in stock_code_res:
                res_list.append(r)

        return res_list

    def getTsInfo(self,trader_id,faccount_id,ccode):
        '''
            获取交易员底仓个股信息
        :param trader_id: 交易员id
        :param faccount_id: 资金账户id
        :param ccode: 股票代码
        :return: 交易底仓股票信息
        '''

        sql = """
            SELECT 
                * 
            FROM oak_trader_stock
            WHERE trader_id='%s' AND account_id='%s' AND ccode='%s'
        """ % (trader_id,faccount_id,ccode)
        res = self._db.selectone(sql)
        return res

    def getDailyCountData(self,trader_id,date):
        '''
        获取某个交易员某日的聚合数据
        聚合数据：
            按股票分组，聚合成交数量（带方向，即单票头寸数量 累计头寸数量），
            发生金额（带方向，即单票盈亏，累计盈亏），当盈亏为正数时，强制为0
        :param trader_id:
        :param date:
        :return:
        '''
        sql = """
            SELECT 
                o.ccode,
                o.cname,
                o.account_id faccount_id,
                sum(if(o.side=0,-1*ifnull(o.dcount,0),ifnull(o.dcount,0))) dcount,
                sum(if(o.side=0,-1*ifnull(o.amount,0),ifnull(o.amount,0))) amount,
                o.odate
            FROM oak_order o 
            WHERE o.odate='%s' AND o.trader_id='%s'
            GROUP BY o.ccode,account_id
        """ % (date, trader_id)
        # print(sql)
        return self._db.selectall(sql)

    def getAccountInfoById(self,account_id):
        sql = """
            SELECT 
                *
            FROM oak_account
            WHERE id='%s'
        """ % (account_id)

        return self._db.selectone(sql)

    def placeOrder(self,params):
        '''
            下单
        '''
        #1.开启事务
        self._db.begin()
        try:
            if int(params['side']) == 0:#买入时
                #1.获取交易员信息，判断余额是否够用
                sql = """
                    select * from oak_trader where id='%s' FOR UPDATE
                """ % (params['trader_id'])
                trader_info = self._db.selectone(sql)

                if trader_info['amount']<params['oamount']:
                    self._db.rollback()
                    return -1

                sql = """
                    update oak_trader set amount=amount-%s where id='%s'
                """ % (params['oamount'], params['trader_id'])
                self._db.execute(sql)

            else:#卖出时
                sql = """
                    select * from oak_trader_stock where id='%s' and trader_id='%s'
                """ % (params['record_id'],params['trader_id'])
                trader_stock = self._db.selectone(sql)
                if trader_stock['acount']<params['ocount']:
                    self._db.rollback()
                    return -2
                sql = """
                    update oak_trader_stock set ucount=ucount-%s where id='%s'
                """ % (params['ocount'], params['record_id'])
                self._db.execute(sql)

            #3.订单入库
            sql = """
                INSERT into oak_order (trader_id,account_id,record_id,type,ccode,cname,
                side,ptype,ocount,oprice,odate,otime,stax,tfee,rfee,mfee,oamount,
                status,slog,ctime,mtime) values('%s','%s','%s','%s','%s',
                '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',
                '%s','%s','%s')
            """ % (params['trader_id'],params['account_id'],params['record_id'],params['type'],params['ccode'],params['cname'],
                params['side'],params['ptype'],params['ocount'],params['oprice'],params['odate'],params['otime'],
                   params['stax'],params['tfee'],params['rfee'],params['mfee'],params['oamount'],
                params['status'],params['slog'],params['ctime'],params['mtime'])
            self._db.execute(sql)
            order_id = self._db.lastrowid()

            self._db.commit()
            return order_id
        except Exception as e:
            self._db.rollback()


    def getAccountByOrderId(self,order_id):
        sql = """
            SELECT 
                a.code account
            FROM
                oak_order o 
            LEFT JOIN oak_account a ON o.account_id=a.id
            WHERE o.id='%s'
        """ % (order_id)
        return self._db.selectone(sql)

    def updateBatchCancelOrder(self,trader_id,order_id_str):
        '''
        批量修改可撤订单为待撤
        :param order_id_str:
        :return:
        '''
        now_time = int(time.time() * 1000)
        #未报 待报 正报 已报 部成
        sql = """
            update oak_order set status='tocancel',mtime='%s'
            WHERE trader_id='%s' AND id IN(%s) AND status IN ('unsend','tosend','sending','sent','pdealt')
        """ % (now_time,trader_id,order_id_str)
        res = self._db.execute(sql)

        return res

    def getBatchCancelOrder(self,trader_id,order_id_str):
        '''
        批量获取可撤订单
        :param order_id_str:
        :return:
        '''
        #未报 待报 正报 已报 部成
        sql = """
            select * from oak_order 
            WHERE trader_id='%s' AND id IN(%s) AND status IN ('unsend','tosend','sending','sent','pdealt')
        """ % (trader_id,order_id_str)
        res = self._db.selectall(sql)
        if res is None:
            return []

        return res

    #获取最大买入数量（考虑过户费 佣金）
    def getBCountWithFee(self,amount,price,transfer_fee_rate,commission_rate,commission_money):
        # print('-----in function-----')
        # print(amount,price,transfer_fee_rate,commission_rate,commission_money)
        count1 = (amount-commission_money)/(price*(1+transfer_fee_rate))
        count1 = math.floor(count1 / 100) * 100
        count2 = amount/(price*(1+transfer_fee_rate+commission_rate))
        count2 = math.floor(count2 / 100) * 100
        # print(count1, count2)
        return min(count1,count2)

    def get_sum_fee(self,oprice,temp_count,buy_rate_config_list):
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

    def getBCountWithFee2(self,cash,oprice,buy_rate_config_list):
        sum_rate = sum([float(item['value']) for item in buy_rate_config_list]) #总费率
        temp_count = self.floor100(cash/(oprice * (1+sum_rate)))#第一次的最大可买数
        temp_cash = oprice * temp_count + self.get_sum_fee(oprice,temp_count,buy_rate_config_list)#第一次计算所需钱数

        while temp_cash < cash:#少了，尝试 +100
            temp_count += 100
            temp_cash = oprice * temp_count + self.get_sum_fee(oprice,temp_count,buy_rate_config_list)

        while temp_cash > cash:#多了，尝试 -100
            temp_count -= 100
            temp_cash = oprice * temp_count + self.get_sum_fee(oprice,temp_count,buy_rate_config_list)

        return temp_count

    def getOneSumAmount(self,trader_id,faccount_id):
        pal = {
            'faccount_id': faccount_id,
            'buy_sum_normal': 0,  # 普通买入
            'buy_sum_margin': 0,  # 两融买入
            'sell_sum_normal': 0,  # 普通卖出
            'sell_sum_margin': 0  # 两融卖出
        }

        performdao = PerformDao()
        lastorderinfo = performdao.getLastOrderInfo()

        if len(lastorderinfo) > 0:
            for loi in lastorderinfo:
                loi['amount'] = loi['amount'] if loi['amount'] is not None else 0
                loi['oamount'] = loi['oamount'] if loi['oamount'] is not None else 0
                if int(loi['faccount_id']) == int(faccount_id):  # 资金账户维度
                    if int(loi['side']) == 0:  # 买入
                        if loi['status'] in ['dealt', 'pcanceled','pexpired']:
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
                        if loi['status'] in ['dealt', 'pcanceled','pexpired']:
                            if loi['otype'] == 'ptmc':  # 非两融
                                pal['sell_sum_normal'] += loi['amount']
                            else:  # 两融
                                pal['sell_sum_margin'] += loi['amount']

        return pal

    def getOneTraderCodeDcountInfo(self, trader_id,faccount_id,ccode):
        sql = """
            select record_id,
            sum(
                case 
                    when side=0 then dcount
                    when side=1 then -1*dcount
                else
                    0
                end
            ) as cash_dcount,
            sum(
                case
                    when side=0 then dcount
                else 
                    0
                end
            ) as bcount,
            sum(
                case
                    when side=1 then dcount
                else 
                    0
                end
            ) as scount
            from oak_order where trader_id='%s' and account_id='%s' and ccode='%s' and `status` in ('dealt','pcanceled','pdealt') and odate >= date_format(now(), '%%Y-%%m-%%d')

        """ % (trader_id,faccount_id,ccode)
        # print(sql)
        return self._db.selectone(sql)

    def getTraderInfoById(self,trader_id):
        sql = '''
            select * from oak_trader where `delete`=0 and id='%s'
        ''' % (trader_id)
        return self._db.selectone(sql)

    def saveMsg(self,type,title,content):
        cur_time = int(time.time() * 1000)
        sql = """
            INSERT INTO
                oak_message (type,title,content,ctime)
            VALUES ('%s','%s','%s','%s')
        """ % (type,title,content,cur_time)
        self._db.execute(sql)
        return self._db.lastrowid()

    def getAllHistoryNewstCash(self,trader_id):
        sql = """
            select tp.trader_id,tp.account_id,ifnull(a.alias,'') fname,tp.scode as ccode,tp.sname as cname,tp.total as ccount from oak_trader_position tp
            left join (select trader_id,account_id,scode,sname,max(pdate) as max_pdate from oak_trader_position  group by trader_id,account_id,scode) as res
            on (res.trader_id=tp.trader_id and res.account_id=tp.account_id and res.scode=tp.scode) 
            left join oak_account as a on tp.account_id=a.id
            where tp.pdate = res.max_pdate and tp.trader_id='%s' and tp.pdate<date_format(now(), '%%Y-%%m-%%d')
            order by tp.account_id asc,tp.scode asc
        """ % (trader_id)
        # print(sql)
        return self._db.selectall(sql)

    def getPositionOrder(self,trader_id):
        '''
            获取交易员当天的买入数量 卖出数量
        '''

        sql = """
            SELECT 
                record_id,
                trader_id,
                account_id,
                ccode,
                side,
                sum(o.dcount) sum_count,
                sum(o.amount) sum_amount from `oak_order` o
            WHERE `trader_id`='%s' and o.`status` in ('dealt','pcanceled') and o.odate>= date_format(now(), '%%Y-%%m-%%d')
            GROUP BY o.account_id,ccode,o.side
        """ % (trader_id)
        # print(sql)
        return self._db.selectall(sql)

    # 获取某只票的最新头寸信息
    def getLastCashInfo(self, trader_id, faccount_id,ccode):
        sql = """
            select * from oak_trader_profit where trader_id='%s' and account_id='%s' and scode='%s' 
            order by `date` desc limit 1
        """ % (trader_id, faccount_id,ccode)

        return self._db.selectone(sql)

    def floor100(self,number):
        return int(float(number) / 100) * 100

    # 获取最大可买可卖数量
    def getBScount2(self,trader_id,faccount_id,ccode,price):
        price = float(price)
        p_info = self.getTraderOnePosition(trader_id, faccount_id, ccode)
        if p_info is None:
            raise trd_no_position_error
        stype = p_info['stype']
        btype = p_info['btype']

        ######################## 预处理数据 #####################
        ### 1.初始化数据
        acount = 0 # 分配数量
        buying_num = 0  # 买入中数量（当前票）
        buy_succ_num = 0  # 买入成功数量（当前票）
        selling_num = 0  # 卖出中数量
        sell_succ_num = 0  # 卖出成功数量
        mbcount = 0 #最大可买数量
        mscount = 0 #最大可卖数量
        cash_count = 0 #头寸股数
        cash_price = 0 #头寸成本
        buy_opening_limit = 0 #买入开仓限额(配置项）
        sell_opening_limit = 0 #卖出开仓限额(配置项）
        buy_opening_limit_left = 0 #买入开仓限额余额
        sell_opening_limit_left = 0 #卖出开仓限额余额
        buy_transit_limit = 0 #买入在途限额（配置项）
        sell_transit_limit = 0 #卖出在途限额（配置项）
        buy_transit_limit_left = 0 #买入在途限额余额
        sell_transit_limit_left = 0 #卖出在途限额余额
        buying_money = 0 #买入中委托金额（所有票）
        selling_money = 0 #卖出中委托金额（所有票）
        ucount = p_info['ucount'] #可卖数量
        buy_opening_money = 0 #买入股票开仓金额（该股票）
        sell_opening_money = 0 #卖出股票开仓金额（该股票）
        buy_opening_money_all = 0 #买入股票开仓金额（所有票）
        sell_opening_money_all = 0 #卖出股票开仓金额（所有票）

        #### 分配数量
        tsinfo = self.getTsInfo(trader_id, faccount_id, ccode)
        acount = tsinfo['acount']

        #### 买入中数量 买入成功数量 卖出中数量 卖出成功数量 买入中委托金额 卖出中委托金额
        status_proccessing_list = [
            'unsend',
            'tosend',
            'sending',
            'sent',
            'pdealt',
            'tocancel',
            'canceling'
        ]
        status_proceed_list = [
            'canceled',
            'pcanceled',
            'dealt',
            'pexpired',
            'expired',
            'cexpired',
        ]
        import datetime
        today = datetime.date.today()
        stimestamp = int(time.mktime(today.timetuple())) * 1000
        order_list = self.getTraderDailyOrder(trader_id, '', True, '', stimestamp)
        for o in order_list:
            ocount = o['ocount1'] if o['ocount1'] is not None else 0
            dcount = o['dcount'] if o['dcount'] is not None else 0

            if o['status'] in status_proccessing_list:  # 进行中
                if o['side'] == 0:  # 买入
                    if o['ccode'] == ccode and int(o['account_id']) == int(faccount_id):#只统计当前票的买入数量
                        buying_num += ocount
                    buying_money += o['ocount'] * float(o['oprice'])#所有票的买入中金额
                else:  # 卖出
                    if o['ccode'] == ccode and int(o['account_id']) == int(faccount_id):#只统计当前票的卖出数量
                        selling_num += ocount
                    selling_money += o['ocount'] * float(o['oprice'])#所有票的卖出中金额
            elif o['status'] in status_proceed_list:  # 终态
                if o['side'] == 0:  # 买入
                    if o['ccode'] == ccode and int(o['account_id']) == int(faccount_id):#只统计当前票的买入数量
                        buy_succ_num += dcount
                else:  # 卖出
                    if o['ccode'] == ccode and int(o['account_id']) == int(faccount_id):#只统计当前票的卖出数量
                        sell_succ_num += dcount
            else:
                pass

        ##获取费率
        account_info = self.getAccountInfoById(faccount_id)
        try:
            account_config = json.loads(account_info['configs'])
            if 'cost' in account_config:
                cost_config = account_config['cost']
            else:#账户没配置，用系统配置
                configdao = ConfigureDao()
                sys_config = configdao.getOneConfig('cost')
                if len(sys_config) <= 0:
                    raise ValueError
                cost_config = sys_config
            if ccode[0] == '6':#sh
                ex = 'sh'
            else: #sz
                ex = 'sz'

            buy_rate_config_list = cost_config['buy'][ex]
        except:
            raise Exception('account data error')

        ##获取配置信息 买入开仓限额 卖出开仓限额 买入在途限额 卖出在途限额
        traderinfo = self.getTraderInfoById(trader_id)
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

        # 获取该交易员"所有票"的头寸信息
        cashinfoall = self.getTraderProfitByDate(trader_id)
        if len(cashinfoall) > 0:
            for cia in cashinfoall:
                if cia['scode'] == ccode and int(cia['account_id']) == int(faccount_id):
                    cash_count = cia['count']
                    cash_price = float(cia['ori_price'])
                    if cia['count'] > 0:
                        buy_opening_money += abs(float(cia['ori_price']) * cia['count'])#股票买入开仓金额（该股票）
                    else:
                        sell_opening_money += abs(float(cia['ori_price']) * cia['count'])#股票卖出开仓金额（该股票）

                if cia['count'] > 0:
                    buy_opening_money_all += abs(float(cia['ori_price']) * cia['count'])#股票买入开仓金额（所有票）
                else:
                    sell_opening_money_all += abs(float(cia['ori_price']) * cia['count'])  # 股票买入开仓金额（所有票）

        #买入开仓限额余额  #买入开仓限额余额 = 买入开仓限额 - sum(abs(买入头寸股数) *头寸成本)   可能为负数
        buy_opening_limit_left = buy_opening_limit - buy_opening_money_all
        # 卖出开仓限额余额  #卖出开仓限额余额 = 卖出开仓限额 - sum(abs(卖出头寸股数) *头寸成本)   可能为负数
        sell_opening_limit_left = sell_opening_limit - sell_opening_money_all
        # 买入在途限额余额  # 买入在途限额余额 = 买入在途限额 - 买入在途金额   可能为负数
        buy_transit_limit_left = buy_transit_limit - buying_money
        # 卖出在途限额余额  # 卖出在途限额余额 = 卖出在途限额 - 卖出在途金额   可能为负数
        sell_transit_limit_left = sell_transit_limit - selling_money

        ################## 最大可买数量 ################
        # 最大可买入数量 = Min【资金户可用资金的最大可买数量，券源可买入数量，开仓限额余额最大可买数量，在途限额最大可买数量】
        # mbcount = min(mb1,mb2,mb3,mb4)  即先求出134的最小资金m13，再求出最小数量mb13，再和mb2 mb4比(注意mb4的计算不同于mb1 mb3)
        # m1资金户可用资金
        suminfo = self.getOneSumAmount(trader_id,faccount_id)
        if stype == 1 and p_info['atype'] == 'margin' and btype == 'rzmr':#两融
            m1 = float(p_info['credit']) + float(suminfo['buy_sum_margin']) + float(suminfo['sell_sum_margin'])
        else: #非两融
            m1 = float(p_info['balance']) + float(suminfo['buy_sum_normal']) + float(suminfo['sell_sum_normal'])

        # mb2 券源可买入数量
        # 券源可买入数量 = 当前已分配数 - 买入终止态委托的已成数量汇总 - 买入中间态委托的委托数量汇总；
        mb2 = acount - buy_succ_num - buying_num

        # m3 买入开仓限额余额
        if cash_count > 0:
            m3 = max(0,buy_opening_limit_left)
        else:
            m3 = max(0,buy_opening_limit_left) + abs(cash_count * cash_price)

        # m4 买入在途限额余额
        m4 = max(0,buy_transit_limit_left)
        mb4 = max(0,self.floor100(m4 / price))

        #mb13
        m13 = min(m1,m3)
        mb13 = self.getBCountWithFee2(float(m13), price,buy_rate_config_list)

        #最大可买数量
        mbcount = max(0,self.floor100(min(mb2,mb13,mb4)))

        ################## 最大可卖出数量 ################
        # 最大可卖＝Min【券源可卖数，开仓限额余额最大可卖，在途限额余额最大可卖，资金户即时可卖数】；
        ###券源可卖数
        ms1 = ucount

        ###卖出开仓限额余额可卖
        if cash_count <= 0:
            ms2 = self.floor100(max(0,sell_opening_limit_left) / price)
        else:
            ms2 = self.floor100((max(0,sell_opening_limit_left) + abs(cash_count * cash_price)) / price)
        ###卖出在途限额余额可卖
        ms3 = max(0,self.floor100(sell_transit_limit_left / price))

        ###资金户即时可卖数
        ms4 = self.getRealSellCount(trader_id,faccount_id,ccode)

        #最大可卖
        mscount = max(0,min(ms1,ms2,ms3,ms4))

        data = {
            'mbcount': mbcount,
            'mscount': mscount
        }
        return data

    # 获取最新的持仓股票收益和头寸
    def getTraderProfitByDate(self, trader_id):
            sql = """
                select 
                    id,trader_id,account_id,scode,sname,count,ifnull(price,0) ori_price,round(ifnull(price,0),2) price,round(ifnull(profit,0),2) profit 
                from oak_trader_profit where trader_id='%s'
            """ % trader_id

            return self._db.selectall(sql)

    # 获取从上一次更新到现在的该票所有委托记录(以持仓表的更新时间为基准)
    def getLastOrderInfoByPosition(self, trader_id,account_id,ccode,mtime,side=''):
        side_sql = ''
        if side != '':
            side_sql = ' and side=%s' % side
        sql = """
                SELECT 
                    o.account_id faccount_id,o.side,o.ocount,o.ocount1,o.dcount,o.dcount1,o.`status`
                from `oak_order` o 
                where o.account_id=%s and ccode='%s' and o.ctime>=%s %s
            """ % (account_id,ccode,mtime,side_sql)
        return self._db.selectall(sql)

    # 获取从上一次更新到现在的该票所有委托记录(以持仓表的更新时间为基准)
    def getAccountPosition(self, account_id, scode):
        sql = """
                SELECT 
                    *
                from oak_account_position ap
                where ap.account_id=%s and ap.scode='%s'
            """ % (account_id,scode)
        return self._db.selectone(sql)

    #获取资金账户的即时可卖数
    def getRealSellCount(self,trader_id,faccount_id,ccode):
        positioninfo = self.getAccountPosition(faccount_id,ccode)
        if positioninfo is None:
            return 0
        lastorderinfo = self.getLastOrderInfoByPosition(trader_id,faccount_id,ccode,positioninfo['mtime'],1) #所有卖出记录
        ori_ucount = positioninfo['ucount'] # 资金户查询的可卖数
        all_order_count = 0 #Sum【卖出实际委托数】
        all_gap_count = 0 #Sum【卖出实际委托数-卖出实际成交数】

        if len(lastorderinfo) > 0:
            for loi in lastorderinfo:
                loi['ocount1'] = loi['ocount1'] if loi['ocount1'] is not None else 0
                loi['dcount1'] = loi['dcount1'] if loi['dcount1'] is not None else 0
                # if loi['status'] in ['unsend', 'tosend', 'sending', 'sent', 'pdealt', 'tocancel', 'canceling']:
                all_order_count += loi['ocount1']
                if loi['status'] in ['dealt', 'pcanceled','pexpired','canceled','expired']:
                    all_gap_count += (loi['ocount1'] - loi['dcount1'])

        real_count = max(0, ori_ucount - all_order_count + all_gap_count)
        return real_count


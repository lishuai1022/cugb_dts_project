from ..mysql import *
from .. import mysqlpool
from .. import config
import json,time
from ..util import checkInput
import datetime

class PerformDao(object):

    def __init__(self):
        self._db = mysqlpool.db
        super().__init__()

    #获取底仓信息
    def getPositionInfo(self,trader_id,status=''):
        status_sql = " a.`status` in ('normal','olimit','bslimit') "  # 全部
        if status != '':
            status_list = status.split(',')
            status_list2 = ["'" + s + "'" for s in status_list if len(s) > 0]
            status_str = ','.join(status_list2)
            status_sql = " a.`status` in (%s) " % status_str
        sql = """
        	SELECT
        		ts.id record_id,ts.trader_id,ts.ccode,ts.cname,ts.acount,
        		a.id faccount_id,a.alias fname,a.balance,a.status,ts.hcount,ts.ucount,a.type as atype,a.btype as btype,ifnull(a.credit,0) credit,ap.credit as stype
        	FROM oak_trader_stock ts
        	LEFT JOIN oak_account a ON ts.account_id=a.id
        	LEFT JOIN oak_account_position ap ON ap.account_id=ts.account_id and ap.scode=ts.ccode
        	WHERE %s and ts.trader_id=%s and (ts.hcount>0 or ts.acount>0)
        	ORDER BY ts.id ASC
        """ % (status_sql,trader_id)
        return self._db.execute_fetchall(sql)

    #获取从上一次更新到现在的所有委托记录(账户维度计算可用余额，不区分trader_id)
    def getLastOrderInfo(self):
        today = datetime.date.today()
        sql = """
            SELECT 
                o.account_id faccount_id,o.side,o.amount,o.oamount,o.`status`,o.`otype` as otype
            from `oak_order` o 
            left join oak_account as ac on o.account_id=ac.id
            where o.ctime>=ac.mtime and o.odate='%s'
        """ % (today)
        return self._db.execute_fetchall(sql)

    #获取今天所有的委托记录
    def getTodayOrderInfo(self, trader_id,source='0'):
        today = time.strftime("%Y-%m-%d")
        source_sql = ' and `source`=0 '
        if source != '0':
            source_sql = ' and `source`=1 '
        sql = """
            select 
                account_id faccount_id,ccode,side,amount,dcount,`status`,ocount,oprice,ocount1
            from oak_order 
            where trader_id=%s and odate >='%s' %s 
        """ % (trader_id,today,source_sql)
        return self._db.execute_fetchall(sql)


    ######################################################################
    #获取历史头寸
    def getHistoryCash(self,trader_id):
        today = time.strftime("%Y-%m-%d")
        sql = '''
            select 
                tp.trader_id,
                tp.account_id faccount_id,
                tp.pdate,
                tp.scode ccode,
                tp.sname cname,
                tp.total ccount
            from oak_trader_position tp 
            right join (
                select 
                    trader_id,account_id,scode,max(pdate) mpdate 
                from oak_trader_position 
                where trader_id=%s and pdate <"%s" group by `trader_id`,`account_id`,scode
            ) a on tp.trader_id=a.trader_id and tp.account_id=a.account_id and tp.scode=a.scode and tp.pdate=a.mpdate
        ''' % (trader_id,today)
        # print(sql)
        return self._db.execute_fetchall(sql)

    #获取当天产生头寸的委托记录
    def getTodayOrderForCash(self,trader_id):
        today = time.strftime("%Y-%m-%d")
        sql = '''
            SELECT 
                o.trader_id,o.account_id as faccount_id,o.ccode,o.cname,o.side,o.`status`,o.dcount,o.ocount,o.clear
            from `oak_order` o 
            where o.trader_id=%s and o.odate>='%s' and `status` in ('dealt','pcanceled','unsend','tosend','sending','sent','pdealt','tocancel','canceling')
        ''' % (trader_id,today)
        return self._db.execute_fetchall(sql)

    def getAccountInfo(self,ids=[]):
        ids_str = ','.join(ids)
        sql = '''
            select id faccount_id,alias as fname from oak_account where `id` in (%s)
        ''' %(ids_str)
        return self._db.execute_fetchall(sql)






    def getTotalCash(self,trader_id,stimestamp):
        sql = """
            select account_id faccount_id,fname,ccode,cname,sum(ccount) ccount from 
            (
                SELECT o.trader_id,o.account_id,ifnull(a.alias,'') fname,o.ccode,o.cname,sum(
                            case 
                                when o.side=0 and o.`status` in ('dealt','pcanceled') then ifnull(dcount,0)
                                when o.clear=0 and o.side=0 and o.`status` in ('unsend','tosend','sending','sent','pdealt','tocancel','canceling') then ifnull(ocount,0)
                                when o.clear=1 and o.side=0 and o.`status` in ('unsend','tosend','sending','sent','pdealt','tocancel','canceling') then ifnull(dcount,0)
                                when o.side=1 and o.`status` in ('dealt','pcanceled') then ifnull(-1*dcount,0)
                                when o.clear=0 and o.side=1 and o.`status` in ('unsend','tosend','sending','sent','pdealt','tocancel','canceling') then ifnull(-1*ocount,0)
                                when o.clear=1 and o.side=1 and o.`status` in ('unsend','tosend','sending','sent','pdealt','tocancel','canceling') then ifnull(-1*dcount,0)
                            else 0
                            end
                        ) as ccount
                        from `oak_order` o left join oak_account as a on o.account_id=a.id
                        where o.account_id is not null and o.trader_id='%s' and o.ctime>='%s' group by o.account_id,o.ccode
                union all
                select tp.trader_id,tp.account_id,ifnull(a.alias,'') fname,tp.scode as ccode,tp.sname as cname,tp.total as ccount from oak_trader_position tp
                left join (select trader_id,account_id,scode,sname,max(pdate) as max_pdate from oak_trader_position  group by trader_id,account_id,scode) as res
                on (res.trader_id=tp.trader_id and res.account_id=tp.account_id and res.scode=tp.scode) 
                left join oak_account as a on tp.account_id=a.id
                where tp.pdate = res.max_pdate and tp.trader_id='%s' and tp.pdate<date_format(now(), '%%Y-%%m-%%d')
            ) as res 
            group by res.account_id,res.ccode      
        """ % (trader_id,stimestamp,trader_id)

        return self._db.execute_fetchall(sql)


    #######################################################################

    def getHolidays(self):
        sql = """
            select value from oak_configure where code='holiday_list'
        """
        res = self._db.execute_fetchone(sql)
        if res is None:
            return []
        return json.loads(res['value'])

    def getTraderDailyOrder2(self, trader_id, item=''):
            '''
                获取交易员"当天"的委托记录
            :param trader_id:交易员id
            :param item:筛选类型 默认为空表示全部 dealt-已成交 canceled-已撤订单 多选时用英文逗号连接
            :param isVirtual:是否包含虚拟记录
            :return:委托记录list
            '''
            import datetime
            today = datetime.date.today()
            condition_sql = ''
            if item == 'can_cancel':  # 可撤单
                condition_sql = " AND o.status IN ('unsend','tosend','sending','sent','pdealt') "
            elif item == 'new_can_cancel':  # 未成委托（新版）
                condition_sql = " AND o.status IN ('unsend','tosend','sending','sent','pdealt','tocancel','canceling') "
            elif item == 'dealt':  # 已成交
                condition_sql = " AND o.status IN ('dealt') "
            elif item == 'canceled':  # 已撤单
                condition_sql = " AND o.status IN ('canceled') "
            elif item == 'canceled,dealt' or item == 'dealt,canceled':  # 已成交 #已撤单
                condition_sql = " AND o.status IN ('canceled','dealt') "
            elif item == 'can_cancel,dealt' or item == 'dealt,can_cancel':  # 已成交 #可撤单
                condition_sql = " AND o.status IN ('dealt','unsend','tosend','sending','sent','pdealt') "
            elif item == 'canceled,can_cancel' or item == 'can_cancel,canceled':  # 可撤单 #已撤单
                condition_sql = " AND o.status IN ('canceled','unsend','tosend','sending','sent','pdealt') "
            else:  # 全部
                pass


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
                    o.dprice,
                    o.dcount,
                    o.cost,
                    o.costs,
                    o.amount,
                    o.ocode,
                    o.`clear`,
                    o.`source`,
                    o.`otype`,
                    a.id faccount_id,
                    a.`alias` fname
            	FROM oak_order o 
            	LEFT JOIN oak_account a ON o.account_id=a.id
    	        WHERE o.odate='%s' AND o.trader_id='%s' %s
    	        ORDER BY o.ctime DESC 
            """ % (today, trader_id, condition_sql)
            return self._db.execute_fetchall(sql)

    def checkTodayTradeDay(self,date):
        d_date = datetime.datetime.strptime(date, '%Y-%m-%d')
        if d_date.weekday() >= 5: #周六日
            return False
        else:
            sql = "select value from oak_configure where code='holiday_list'"
            res = self._db.execute_fetchone(sql)
            if res is None:
                res = []
            else:
                res = json.loads(res['value'])
            if date in res:
                return False
        return True

    #获取最新的持仓股票收益和头寸
    def getTraderProfitByDate(self,trader_id,source='0'):
        source_sql = ' and `source`=0 '
        if source != '0':
            source_sql = ' and `source`=1 '
        sql = """
            select 
                id,trader_id,account_id,scode,sname,count,ifnull(price,0) ori_price,round(ifnull(price,0),2) price,round(ifnull(tprofit,0),2) tprofit 
            from oak_trader_profit where trader_id='%s' %s
        """ % (trader_id,source_sql)

        return self._db.execute_fetchall(sql)

    # 获取头寸
    def getTraderProfitList(self, trader_id):
        sql = """
            select 
                tp.id,
                tp.trader_id,
                tp.account_id as faccount_id,
                tp.scode ccode,
                tp.sname cname,
                a.`alias` as fname,
                tp.count cash_count,
                ifnull(tp.price,0) ori_price,
                round(ifnull(tp.price,0),2) cash_price,
                round(ifnull(tp.tprofit,0),2) deal_profit,
                tp.`source` 
            from oak_trader_profit  as tp 
            left join oak_account a on a.id=tp.account_id 
            where tp.trader_id='%s' and tp.`count`!=0
        """ % trader_id
        # print(sql)
        return self._db.execute_fetchall(sql)
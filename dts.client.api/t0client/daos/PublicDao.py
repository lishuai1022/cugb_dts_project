from ..mysql import *
from .. import mysqlpool
from .. import config
import json,time
from ..util import checkInput
import datetime
from ..util.miscUtil import *

class PublicDao(object):
    def __init__(self):
        self._db = mysqlpool.db
        super().__init__()

    ######################## 公共券池列表 S###################################
    #获取公共券池底仓信息
    def getPublicPositionInfo(self,status=''):
        status_sql = " a.`status` in ('normal','olimit','bslimit') " #全部
        if status != '':
            status_list = status.split(',')
            status_list2 = ["'" + s + "'" for s in status_list if len(s) > 0]
            status_str = ','.join(status_list2)
            status_sql = " a.`status` in (%s) " % status_str
        sql = """
        	SELECT
        		ps.id as record_id,
        		ps.scode as ccode,
        		ps.sname as cname,
        		ps.acount,
        		ps.hcount,
        		ps.ucount,
        		ps.ocount,
        		a.id faccount_id,
        		a.alias fname,
        		a.balance,
        		a.type as atype,
        		a.btype as btype,
        		ifnull(a.credit,0) credit,
        		a.status,
        		ap.credit as stype
        	FROM oak_public_stock ps
        	LEFT JOIN oak_account a ON ps.account_id=a.id
        	LEFT JOIN oak_account_position ap ON ap.account_id=ps.account_id and ap.scode=ps.scode
        	WHERE %s and (ps.hcount>0 or ps.acount>0)
        	ORDER BY ps.id ASC
        """ % status_sql
        return self._db.execute_fetchall(sql)

    # 获取从上一次更新到现在的所有委托记录（账户维度，不区分trader_id）
    def getPublicAllLastOrderInfo(self):
        today = time.strftime("%Y-%m-%d")
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
            where o.odate='%s' and o.ctime>=ac.mtime 
        """ % (today)
        return self._db.execute_fetchall(sql)

    # 获取今天所有的委托记录
    def getPublicTodayOrderInfo(self, trader_id):
        today = time.strftime("%Y-%m-%d")
        source_sql = ' and `source`=1 '
        sql = """
            select 
                account_id faccount_id,ccode,side,amount,dcount,`status`,ocount,oprice,ocount1
            from oak_order 
            where trader_id=%s and odate='%s' %s 
        """ % (trader_id, today, source_sql)
        return self._db.execute_fetchall(sql)

    # 获取最新的持仓股票收益和头寸
    def getPublicTraderProfitByDate(self, trader_id):
        source_sql = ' and `source`=1 '
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
                round(ifnull(tprofit,0),2) tprofit 
            from oak_trader_profit 
            where trader_id='%s' %s
        """ % (trader_id, source_sql)

        return self._db.execute_fetchall(sql)

    ######################## 公共券池列表 E###################################

    ######################## 其他 ###################################
    def newSearchStock(self,keyword=''):
        '''
            股票搜索
        '''

        keyword = keyword.strip()
        if keyword == '':
            return []
        #请求外部接口，获取股票集合
        all_stock_list = getAllStocks()
        stock_code_res = []
        for s in all_stock_list:
            if s['code'].find(keyword) >= 0 \
                    or s['pinyin1'].find(keyword.upper()) >= 0\
                    or s['name'].find(keyword) >= 0 \
                    or s['pinyin2'].find(keyword.upper()) >= 0:
                stock_code_res.append({'ccode':s['code'],'cname':s['name']})
        stock_code_res = stock_code_res[:20]

        return stock_code_res

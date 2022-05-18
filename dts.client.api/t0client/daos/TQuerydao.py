from ..mysql import *
import logging

class TQueryDao(object):
    def __init__(self):
        self._db = DBMysql()
        super().__init__()

    def getAccountInfo(self, taccount_id):
        '''获取账户信息'''
        sql = """
             SELECT
              taccount_id,
              (lmoney+fmoney) as money,
              fmoney,
              lmoney,
              wmoney,
              pmoney,
              capital,
              margin,
              cmargin,
              status
              FROM oak_transaction_account
              WHERE taccount_id='%s'""" % (taccount_id)
        return self._db.selectone(sql)

    def getPosition(self,taccount_id):
        '''获取持仓'''
        sql = """
            SELECT
                p.position_id,
                p.taccount_id,
                s.code,
                s.name,
                round(p.hprice,4) hprice,
                p.hcount,
                p.ucount,
                s.delist
            FROM oak_taccount_position AS p
            LEFT JOIN oak_stock s ON s.code=p.ccode
            WHERE taccount_id='%s' AND p.hcount > 0
            ORDER BY p.ctime DESC
        """ % (taccount_id)
        # print(sql)
        return self._db.selectall(sql)

    def getCancelCount(self,taccount_id):
        '''获取撤单总数'''
        sql = """
            SELECT 
                count(*) total
            FROM oak_taccount_order
            WHERE taccount_id='%s' AND `clear`=0 AND status IN ('unsend','tosend','sending','sent','tocancel','canceling','pdealt') 
        """ % (taccount_id)
        res = self._db.selectone(sql)
        return res['total']

    def getCancelList(self,taccount_id,page=1,pagesize=20):
        '''获取撤单列表'''
        limit = (int(page) - 1) * int(pagesize)
        limit_sql = 'limit %s,%s' % (limit, pagesize)
        sql = """
            SELECT 
                torder_id,
                taccount_id,
                ccode,
                cname,
                side,
                ptype,
                FROM_UNIXTIME(otime/1000,'%%Y-%%m-%%d %%H:%%i:%%s') otime,
                oprice,
                dprice,
                ocount,
                dcount,
                status
            FROM oak_taccount_order
            WHERE taccount_id='%s' AND `clear`=0 AND status IN ('unsend','tosend','sending','sent','tocancel','canceling','pdealt') 
            ORDER BY ctime DESC
            %s
        """ % (taccount_id,limit_sql)
        return self._db.selectall(sql)

    def getOrderCount(self,taccount_id,stimestamp='',etimestamp='',item='all'):
        '''获取委托总数'''
        if str(item) == 'orderbuy':
            side_sql = ' AND side=0 '
        elif str(item) == 'ordersell':
            side_sql = ' AND side=1 '
        else:
            side_sql = ''

        sql = """
            SELECT 
                count(*) total
            FROM oak_taccount_order
            WHERE taccount_id='%s'  %s AND ctime>='%s' AND ctime<='%s'
        """ % (taccount_id,side_sql,stimestamp,etimestamp)

        logging.info(sql)
        res = self._db.selectone(sql)
        return res['total']

    def getOrderList(self,taccount_id,stimestamp='',etimestamp='',page=1,pagesize=20,item='all'):
        '''获取委托列表'''
        limit = (int(page) - 1) * int(pagesize)
        limit_sql = 'limit %s,%s' % (limit, pagesize)

        if str(item) == 'orderbuy':
            side_sql = ' AND side=0 '
        elif str(item) == 'ordersell':
            side_sql = ' AND side=1 '
        else:
            side_sql = ''

        sql = """
            SELECT 
                torder_id,
                taccount_id,
                dcode,
                ccode,
                cname,
                side,
                ptype,
                FROM_UNIXTIME(otime/1000,'%%Y-%%m-%%d %%H:%%i:%%s') otime,
                oprice,
                dprice,
                ocount,
                dcount,
                status
            FROM oak_taccount_order
            WHERE taccount_id='%s'  %s AND ctime>='%s' AND ctime<='%s'
            ORDER BY ctime DESC
            %s
        """ % (taccount_id,side_sql,stimestamp,etimestamp,limit_sql)
        logging.info(sql)
        return self._db.selectall(sql)

    def getOrderListImport(self,taccount_id,stimestamp='',etimestamp='',item='all'):
        '''获取委托列表'''

        if str(item) == 'orderbuy':
            side_sql = ' AND side=0 '
        elif str(item) == 'ordersell':
            side_sql = ' AND side=1 '
        else:
            side_sql = ''

        sql = """
            SELECT 
                torder_id,
                taccount_id,
                dcode,
                ccode,
                cname,
                if(side=0,'买入','卖出') as side,
                ptype,
                FROM_UNIXTIME(otime/1000,'%%Y-%%m-%%d %%H:%%i:%%s') otime,
                oprice,
                dprice,
                ocount,
                dcount,
                status
            FROM oak_taccount_order
            WHERE taccount_id='%s'  %s AND ctime>='%s' AND ctime<='%s'
            ORDER BY ctime DESC
        """ % (taccount_id,side_sql,stimestamp,etimestamp)
        return self._db.selectall(sql)


    def getFillCount(self,taccount_id,stimestamp='',etimestamp='',item='all'):
        '''获取成交总数'''
        if str(item) == 'orderbuy':
            side_sql = ' AND vor.side=0 '
        elif str(item) == 'ordersell':
            side_sql = ' AND vor.side=1 '
        else:
            side_sql = ''
        sql = """
            SELECT 
                count(*) total
            FROM oak_vaccount_order_record vor
            LEFT JOIN oak_virtual_account va ON va.vaccount_id=vor.vaccount_id
            WHERE va.taccount_id='%s' %s AND vor.ctime>='%s' AND vor.ctime<='%s'
        """ % (taccount_id,side_sql,stimestamp,etimestamp)

        res = self._db.selectone(sql)
        print(sql)
        return res['total']

    def getFillList(self,taccount_id,stimestamp='',etimestamp='',page=1,pagesize=20,item='all'):
        '''获取成交列表'''
        limit = (int(page) - 1) * int(pagesize)
        limit_sql = 'limit %s,%s' % (limit, pagesize)

        if str(item) == 'orderbuy':
            side_sql = ' AND vor.side=0 '
        elif str(item) == 'ordersell':
            side_sql = ' AND vor.side=1 '
        else:
            side_sql = ''

        sql = """
            SELECT 
                vor.record_id,
                va.taccount_id,
                `to`.dcode,
                vor.ccode,
                vor.cname,
                vor.side,
                FROM_UNIXTIME(vor.dtime/1000,'%%Y-%%m-%%d %%H:%%i:%%s') dtime,
                vor.dprice,
                vor.dcount,
                vor.amount
            FROM oak_vaccount_order_record vor
            LEFT JOIN oak_virtual_account va ON va.vaccount_id=vor.vaccount_id
            LEFT JOIN oak_taccount_order `to` ON `to`.torder_id=vor.torder_id
            WHERE va.taccount_id='%s' %s AND vor.ctime>='%s' AND vor.ctime<='%s' 
            ORDER BY vor.ctime DESC,record_id DESC 
            %s
        """ % (taccount_id,side_sql,stimestamp,etimestamp,limit_sql)
        print(sql)
        return self._db.selectall(sql)

    def getFillListImport(self,taccount_id,stimestamp='',etimestamp='',item='all'):
        '''获取成交列表'''
        if str(item) == 'orderbuy':
            side_sql = ' AND vor.side=0 '
        elif str(item) == 'ordersell':
            side_sql = ' AND vor.side=1 '
        else:
            side_sql = ''

        sql = """
            SELECT 
                vor.record_id,
                va.taccount_id,
                `to`.dcode,
                vor.ccode,
                vor.cname,
                if(vor.side=0,'买入','卖出') as side,
                FROM_UNIXTIME(vor.dtime/1000,'%%Y-%%m-%%d %%H:%%i:%%s') dtime,
                vor.dprice,
                vor.dcount,
                vor.amount
            FROM oak_vaccount_order_record vor
            LEFT JOIN oak_virtual_account va ON va.vaccount_id=vor.vaccount_id
            LEFT JOIN oak_taccount_order `to` ON `to`.torder_id=vor.torder_id
            WHERE va.taccount_id='%s' %s AND vor.ctime>='%s' AND vor.ctime<='%s' 
            ORDER BY vor.ctime DESC,record_id DESC 
        """ % (taccount_id,side_sql,stimestamp,etimestamp)
        print(sql)
        return self._db.selectall(sql)

    def getMoneyCount(self,taccount_id,item='all',sdate='',edate=''):
        '''获取资金流水总数'''
        if str(item) == 'all':
            item_sql = ""
        else:#全部
            item_sql = " AND item='%s' " % (item)

        sql = """
            SELECT 
                count(*) total
            FROM oak_money_detail 
            WHERE taccount_id='%s' %s AND FROM_UNIXTIME(ctime/1000,'%%Y-%%m-%%d')>='%s' AND FROM_UNIXTIME(ctime/1000,'%%Y-%%m-%%d')<='%s'
        """ % (taccount_id,item_sql,sdate,edate)
        res = self._db.selectone(sql)
        return res['total']

    def getMoneyList(self,taccount_id,item='orderbuy',sdate='',edate='',page=1,pagesize=20):
        '''获取资金流水列表'''
        if str(item) == 'all':
            item_sql = ""
        else:#全部
            item_sql = " AND item='%s' " % (item)

        limit = (int(page) - 1) * int(pagesize)
        limit_sql = 'limit %s,%s' % (limit, pagesize)

        sql = """
            SELECT 
                detail_id,
                taccount_id,
                code,
                item,
                `name`,
                detail,
                money,
                FROM_UNIXTIME(ctime/1000,'%%Y-%%m-%%d %%H:%%i:%%s') ctime
            FROM oak_money_detail 
            WHERE taccount_id='%s' %s AND FROM_UNIXTIME(ctime/1000,'%%Y-%%m-%%d')>='%s' AND FROM_UNIXTIME(ctime/1000,'%%Y-%%m-%%d')<='%s'
            ORDER BY ctime DESC 
            %s
        """ % (taccount_id,item_sql,sdate,edate,limit_sql)
        print(sql)
        return self._db.selectall(sql)

    def getMoneyListImport(self,taccount_id,item='orderbuy',sdate='',edate=''):
        '''获取资金流水列表'''
        if str(item) == 'all':
            item_sql = ""
        else:#全部
            item_sql = " AND item='%s' " % (item)

        sql = """
            SELECT 
                detail_id,
                taccount_id,
                code,
                item,
                `name`,
                detail,
                money,
                FROM_UNIXTIME(ctime/1000,'%%Y-%%m-%%d %%H:%%i:%%s') ctime
            FROM oak_money_detail 
            WHERE taccount_id='%s' %s AND FROM_UNIXTIME(ctime/1000,'%%Y-%%m-%%d')>='%s' AND FROM_UNIXTIME(ctime/1000,'%%Y-%%m-%%d')<='%s'
            ORDER BY ctime DESC 
        """ % (taccount_id,item_sql,sdate,edate)
        print(sql)
        return self._db.selectall(sql)

    def getConfiginfo(self,taccount_id):
        '''获取配置信息'''
        list1 = {
            "money_limit",
            "number_limit",
            "start_one_position_ratio",
            "start_position_ratio",
            "sme_one_position_ratio",
            "sme_position_ratio",
            "other_one_position_ratio",
        }
        sql = """
            SELECT 
                code,
                `value`
            FROM oak_taccount_configure
            WHERE taccount_id='%s'
        """ % (taccount_id)

        res = self._db.selectall(sql)

        ret = {}
        for v in res:
            code = v.get('code')
            value = v.get('value')
            if code in list1:
                ret[code] = value
        # print(ret)
        return ret

    def searchStock(self,keyword):
        if not keyword:
            return []

        word, t = self.parse_word_type(keyword)
        word = word.replace(" ", "").replace("　", "")
        if t is None:
            return []
        wheres = self.get_where(t, word)

        where = " OR ".join(wheres)
        sql = """
              SELECT 
                code, 
                `name`, 
                delist, 
                status
              FROM oak_stock
              WHERE %s
              LIMIT 20
            """ % (where)
        print(sql)
        return self._db.selectall(sql)

    def parse_word_type(self, word):
        word = word.replace(" ", "").replace(" ", "")

        if word[0] >= u"\u4e00" and word[0] <= u"\u9fa5":
          return word, "chinese"

        if word[0] >= u'\u0030' and word[0] <= u'\u0039':
          return word, "number"

        if (word[0] >= u'\u0041' and word[0]<=u'\u005a') or (word[0] >= u'\u0061' and word[0]<=u'\u007a'):
          return word.upper(), "pinyin"

        return word, None

    def get_where(self, t, word):
        field_config = {
            "chinese": ["name"],
            "number": ["code"],
            "pinyin": ["pinyin1", "pinyin2"],
        }
        field = field_config[t]
        wheres = []
        for f in field:
            wheres.append(" %s LIKE '%%%s%%'" % (f, word))

        return wheres

    def getStockPosition(self,taccount_id,code):
        sql = """
            SELECT 
                hcount,
                ucount
            FROM oak_taccount_position
            WHERE taccount_id='%s' AND `ccode`='%s'
        """ % (taccount_id,code)

        return self._db.selectone(sql)

    def getBuyTransitMoney(self,taccount_id):
        status_list = ['tosend', 'sending', 'sent', 'tocancel', 'canceling', 'pdealt']
        status_str = ",".join("'"+str(i)+"'" for i in status_list)
        logging.info(status_str)
        sql = """
            select taccount_id, sum(oamount) as total_amount 
            from oak_taccount_order  where 
            taccount_id = %s and side=0 and `clear`=0 and amount is null and status in (%s)
        """ % (taccount_id,status_str)

        logging.info(sql)
        res = self._db.selectone(sql)
        logging.info(res)

        if res is None or res['total_amount'] is None:
            return '0.00'
        else:
            return res['total_amount']



from ..mysql import *
from ..util import *

class TraderDao(object):
    def __init__(self):
        self._db = DBMysql()
        super().__init__()

    def verifyPwd(self, account, pwd):
        password = checkInput.getPwd(pwd)
        sql = """
            select * from oak_trader where account='%s' and password='%s' and `delete`=0
        """ % (account, password)
        print(sql)
        return self._db.selectone(sql)

    def verifyPwdByTraderId(self, trader_id, pwd):
        pwd = checkInput.getPwd(pwd)
        sql = """
            select * from oak_trader where id='%s' and password='%s' and `delete`=0
        """ % (trader_id, pwd)
        # print(sql)
        return self._db.selectone(sql)

    def changePwd(self, trader_id, old_pwd, new_pwd):
        old_pwd = checkInput.getPwd(old_pwd)
        new_pwd = checkInput.getPwd(new_pwd)
        sql = """
            UPDATE oak_trader set password='%s' where id='%s' and password='%s' and `delete`=0
        """ % (new_pwd, trader_id, old_pwd)
        return self._db.execute(sql)

    def getTraderAccount(self,trader_id):
        sql = """
            select 
                *
            from oak_trader
            where id='%s' and `delete`=0
        """ % (trader_id)
        return self._db.selectone(sql)

    def getSecretKey(self,account):
        sql = """
            select 
                ta.skey
            from oak_trader t
            left join oak_transaction_account ta on t.taccount_id=ta.taccount_id
            where t.account='%s'
        """ % (account)
        res = self._db.selectone(sql)

        if res is None:
            return ''

        return res['skey']

    def getTraderStock(self,trader_id,ccode,faccount_id):
        sql = """
            SELECT 
                * 
            FROM oak_trader_stock 
            WHERE trader_id='%s' AND ccode='%s' AND account_id='%s'
        """ % (trader_id,ccode,faccount_id)
        res = self._db.selectone(sql)
        return res

    def getInfoByAccount(self, account):
        sql = """
            select id from oak_trader where account='%s' and `delete`=0
        """ % (account)
        # print(sql)
        return self._db.selectone(sql)






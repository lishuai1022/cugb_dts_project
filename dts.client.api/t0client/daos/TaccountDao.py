from ..mysql import *

class TaccountDao(object):
    def __init__(self):
        self._db = DBMysql()
        super().__init__()

    def getInfoByAccount(self,account):
        sql = """
            select * from oak_transaction_account where `delete`=0 and account='%s'
        """ % (account)
        return self._db.selectone(sql)

    def getAccountSecretkey(self,taccount_id):
        sql = """
            select * from oak_taccount_configure where taccount_id='%s' and code = 'secret_key'
        """ % (taccount_id)
        return self._db.selectone(sql)



from . import BaseModel

class UserModel (BaseModel):
    def changepwd(self,taccount_id,old_pwd,new_pwd):
        sql = "UPDATE oak_transaction_account set password='%s' where taccount_id='%s' and password='%s'" %(new_pwd,taccount_id,old_pwd)
        return self._db.execute(sql)

    def verifypwd(self,taccount_id,pwd):
        sql = "select * from oak_transaction_account where taccount_id='%s' and password='%s'" % (taccount_id, pwd)
        return self._db.query(sql)


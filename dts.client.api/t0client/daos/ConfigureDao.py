from ..mysql import *
import json

class ConfigureDao(object):
    def __init__(self):
        self._db = DBMysql()
        super().__init__()

    def getHolidays(self):
        sql = """
            select value from oak_configure where code='holiday_list'
        """
        res = self._db.selectone(sql)
        if res is None:
            return []
        return json.loads(res['value'])

    def getOneConfig(self,code):
        sql = """
                    select value from oak_configure where code='%s'
                """ % (code)
        res = self._db.selectone(sql)
        if res is None:
            return {}
        return json.loads(res['value'])


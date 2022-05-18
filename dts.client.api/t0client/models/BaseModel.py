'''
模型父类
'''
from .. import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..config.config import *
# from ..util.mydb import *
# from ..util.log import *

class BaseModel():

    def __init__(self):
        self.domain = config.TRADE_SERVER_DOMAIN
        self.url_config = config.TRADE_URL_CONFIG

        # self._db = connect_peizi_db()

    def __del__(self):
        pass
        # self._db.close()
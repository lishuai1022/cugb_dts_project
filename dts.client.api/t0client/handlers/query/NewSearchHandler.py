from ... import access, forms
from ...error import *
from ..AuthHandler import AuthHandler
import time,datetime
from ...daos.PublicDao import *

class NewSearchHandler(AuthHandler):
    @access.exptproc
    def get(self):
        ccode = self.get_argument('ccode', '')


        publicdao = PublicDao()
        res = publicdao.newSearchStock(ccode)
        self.write(protocol.success(data=res))
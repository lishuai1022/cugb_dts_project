from ... import access, forms
from ...error import *
from ..AuthHandler import AuthHandler
from ...daos.TQuerydao import *

class DcancelHandler(AuthHandler):
    @access.exptproc
    def get(self):
        print(self.arguments)
        form = forms.query.Cancel(**self.arguments)

        page = self.get_argument('page',1)
        pagesize = self.get_argument('pagesize',20)
        taccount_id = self.taccount_id
        tquerydao = TQueryDao()
        total = tquerydao.getCancelCount(taccount_id)
        datalist = tquerydao.getCancelList(taccount_id,page,pagesize)
        data = {
            "total":total,
            "page":page,
            "pagesize":pagesize,
            "list":datalist
        }
        self.write(protocol.success(data=data))
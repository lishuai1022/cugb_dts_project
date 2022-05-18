from .. import AuthHandler
from ... import access, protocol, forms
from ...util.miscUtil import *
import tornado.web

class TestHandler(tornado.web.RequestHandler):
    # @access.exptproc
    def get(self):
        arr = [
            {
                'ccount': '-200',
                'ccode': '600031',

            },
            {
                'ccount': '100',
                'ccode': '300111',

            }
        ]
        data = getVirtualCMoney(arr)
        # form = forms.login.Login(**self.arguments)
        #
        # data = {'account':form.account,'pwd':form.pwd}
        # data = {'aaa':1111}

        self.write(protocol.success(data=data))
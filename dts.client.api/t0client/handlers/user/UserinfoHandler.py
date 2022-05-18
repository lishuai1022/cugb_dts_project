from ... import access,protocol
from ..AuthHandler import AuthHandler
import json

class UserinfoHandler(AuthHandler):
    @access.exptproc
    def get(self):
        traderinfo = self.traderinfo
        try:
            trader_config = json.loads(traderinfo['configs'])
            position_limit = '0'
            if 'position_limit' in trader_config.keys():
                position_limit = trader_config['position_limit']
            public_stock = '0'
            if 'public_stock' in trader_config.keys():
                public_stock = trader_config['public_stock']
        except:
            raise Exception('trader data error')

        data = {
            'trader_id':traderinfo['id'],
            'account':traderinfo['account'],
            'name':traderinfo['name'],
            'iamount':traderinfo['iamount'],
            'amount':position_limit,
            'status':traderinfo['status'],
            'public_stock':public_stock
        }
        self.write(protocol.success(data=data))
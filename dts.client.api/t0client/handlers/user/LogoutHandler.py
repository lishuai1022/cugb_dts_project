from ... import access,protocol
from ..AuthHandler import AuthHandler

class LogoutHandler(AuthHandler):
    @access.exptproc
    def get(self):
        client_key = self.getUserTokenKey(self.trader_id)
        self.redis.delete(client_key)
        self.write(protocol.success())
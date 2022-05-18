"""
    access protection
"""
import logging, tornado.web
from . import error, config, protocol, token
import traceback
from .base import validator,field
from .util.DingTalk import *
from .config.config import *
from .daos.OrderDao import *

def needtoken(handler_func):
    """
        handler access protection
    :param handler_func:
    :return:
    """
    def wrapper(self, *args, **kwargs):
        if config.ENABLE_KEY and not token.validate(self.arguments, config.PRIVATE_KEY):
            self.write(error.invalid_access.data)
        else:
            return handler_func(self, *args, **kwargs)

    return wrapper

def sendDing(e):
    pass
    #dingtalk = DingTalk()
    #dingtalk.send(DINGDING_AMS_TOKEN, str(e))
    # logging.error(str(e))

def saveMsg(e):

    if isinstance(e,dict):
        status = e['ret_code']
        msg = json.dumps(e)
        type = 'channel_api'
    elif isinstance(e,error.ProcessError):
        status = e.status
        msg = e.msg
        type = 'error'
    else:
        return

    orderdao = OrderDao()
    orderdao.saveMsg(type,status,msg)


def exptproc(handler_func):
    def wrapper(self, *args, **kwargs):
        try:
            return handler_func(self, *args, **kwargs)
        except tornado.web.MissingArgumentError as e:
            self.write(error.missing_parameters.data)
            saveMsg(e)
            sendDing(e)
            self.finish()
        except error.ProcessError as e:
            self.write(e.data)
            saveMsg(e)
            sendDing(e)
            self.finish()
        except field.ErrorFieldValue as e:
            self.write(error.invalid_parameters.data)
            saveMsg(e)
            sendDing(e)
            self.finish()
        except Exception as e:
            self.write(error.error_common_exception)
            saveMsg(e)
            sendDing(e)
            self.finish()
    return wrapper

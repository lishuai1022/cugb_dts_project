"""
    protocol for quote service
"""
import json, datetime
from decimal import Decimal

class JEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        elif isinstance(o, datetime.datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(o, datetime.date):
            return o.strftime("%Y-%m-%d")

        return super(JEncoder, self).default(o)

def json_encode(values):
    """
        转换为json格式
    """
    return json.dumps(values, cls=JEncoder)

def success(status=0,msg = 'ok', data = {}):
    """
        error return format
    :param msg:
    :return:
    """
    # make formatted return
    ret = {
        'status': status,
        'msg': msg,
        'data': data
    }

    return json.dumps(ret, cls=JEncoder)


def failed(status=-1, msg = 'failed', data = {}):
    """
        error return format
    :param msg:
    :return:
    """
    # make formatted return
    ret = {
        'status': status,
        'msg': msg,
        'data': data
    }

    return json.dumps(ret, cls=JEncoder)

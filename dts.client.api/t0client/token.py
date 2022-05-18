"""
    token generator & validator form parameters
"""
import time, hashlib
from .config import *
from .rds import rds_cli
from .daos import TraderDao
import json


def generate(params, key):
    """
        add token to params
    :param params: dict
    :param key: str
    :return:
        dict, params with _tm/_token items added
    """
    # current timestamp
    timenow = str(int(time.time()))

    # sorted values
    values = []
    for value in params.values():
        if value is not None:
            values.append(str(value))
    values.sort()

    # value string
    valuestr = ''.join(values)

    # key string
    keystr = valuestr+timenow+key

    # generate token
    token = hashlib.sha1(keystr.encode()).hexdigest()

    # create new params
    params['_tm'] = timenow
    params['_token'] = token[20:]

    return params


def validate(params, key):
    """
        check token
    :param params: dict
    :param key: str
    :return:
        True for validate passed, otherwise False
    """
    # check parameters
    if '_tm' not in params.keys() or '_token' not in params.keys():
        return False

    # get timestamp
    timenow = params['_tm']

    # get token
    token = params['_token']

    # sorted values
    values = []
    for k, v in params.items():
        if k not in ['_tm', '_token']:
            values.append(str(v))
    values.sort()

    # value string
    valuestr = ''.join(values)

    # key string
    keystr = valuestr+timenow+key

    # generate token
    ctoken = hashlib.sha1(keystr.encode()).hexdigest()[20:]

    if token == ctoken:
        return True

    return False

# def getSign(params):
#     print('========')
#     print(params)
#     print('========')
#     if 'sign' in params.keys():
#         params.pop('sign')
#     sign_key = config.SIGN_KEY
#     str1 = ''
#     for arg in sorted(params.items(), key=lambda x: x[0]):
#         str1 += str(arg[1])
#     str1 = sign_key + str1
#     print('----------')
#     print(str1)
#     print('----------')
#     return hashlib.md5(str1.encode()).hexdigest()

def getKey(trader_id):
    # key = rds_cli.hget(config.TRAN_SECRET_HASH, account)
    traderDao = TraderDao.TraderDao()
    traderInfo = traderDao.getTraderAccount(trader_id)
    configs = json.loads(traderInfo['configs'])
    key = configs.get('skey')
    return key

def getSign(plist):
    # key = getKey(plist['trader_id'])
    key = config.AMS_TRAN_KEY

    # print('----------')
    # print(plist)
    # print('----------')
    # print('key='+key)
    all_val = str(key)
    for param in sorted(plist):
        if param != 'sign':
            all_val = all_val + str(plist[param])
    sign = hashlib.md5(all_val.encode(encoding='UTF-8')).hexdigest()
    return sign

def getToken(account):
    token_key = config.TOKEN_KEY
    tm = str(int(time.time()))
    str1 = token_key + str(account) + tm
    return hashlib.md5(str1.encode()).hexdigest()

if __name__ == '__main__':
    print(getToken('aaa'))
    param = {
        'a':'1',
        'b':2,
    }
    print(getSign(param))
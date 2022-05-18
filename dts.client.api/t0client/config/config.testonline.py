"""
    app config
"""
# running mode
import os
MODE = "testonline"

# configure for tornado appliaction
DEBUG = False
AUTORELOAD = False

# database configure
DBNAMES = {
	"peizi" : "db_dts"
}

DATABASES = {
    'peizi': {
        'host': 'rm-2zeartp1lr6li6n32.mysql.rds.aliyuncs.com',
        'user': 'rwtrans',
        'password': 'Ka0BghewhXc2OXp7',
        'port': 3306,
        'charset': 'utf8',
        'database': 'db_dts',
        'autocommit': True
    }
}

##################################################3

#token key
TOKEN_KEY = 'trader_aokebaer'
#sign key
SIGN_KEY = b'test1@OakBarrel'

#trade_api_url
TRADE_SERVER_DOMAIN = 'http://test.fapi.am.youlikj.com'
TRADE_URL_CONFIG = {
    'TRADE_ORDER_PLACE' : '/api/v1/ftrd/order',
    'TRADE_ORDER_CANCEL' : '/api/v1/ftrd/cancel',
}
TRADE_REDIS_HASH = 'traderapi_token_'

#验证码
RESOURCE_PATH = os.path.dirname(__file__)+'/../resource'
CAPTCHA_FONT = RESOURCE_PATH + '/windows/luxirb.ttf'
CAPTCHA_BGPATH = RESOURCE_PATH + '/image/'
CAPTCHA_TIMEOUT = 180
CAPTCHA_CODE_REDIS_PREFIX = 't0trade_imgcode_'
CAPTCHA_TIME_REDIS_PREFIX = 't0trade_imgcode_time_'

#前端token
CLIENT_TOKEN_KEY_PREFIX = 't0trade_client_token_'
CLIENT_TOKEN_AUTH_KEY = 't0trade_client_aokebaer'
BACKEND_TOKEN_KEY_PREFIX = 't0trade_backend_token_'

#密码加密key
SECRET_KEY = 'oak@peizi_2018'

#通讯redis的hash名
TRAN_SECRET_HASH = 't0trade_trans_hash'

HQ_DOMAIN = 'http://test.sq.youlikj.com'

#DingDing机器人token
DINGDING_AMS_TOKEN = 'd76bda6aab1e1088dfff13f0b693d5c0e883e8abb9e90fcead8609473e1ec537'

#交易通道key
AMS_TRAN_KEY = 'dts@oak_2019@AMS-dev'

#后端配置
DTS_DOMAIN = 'http://open.dts.youlikj.com'
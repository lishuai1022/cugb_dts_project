"""
    public app config
"""
import sys
if sys.platform == 'win32':
    r_path = r'C:\Users\admin\Desktop\lishuai'
else:
    r_path = ''
# private key for access
ENABLE_KEY = True
PRIVATE_KEY = 'abc'

# cookie expire time in seconds
COOKIE_SECRET = 'abc'
COOKIE_TIMEOUT = 30*24*3600

# public headers for response
HEADERS = [
    ('Content-Type', 'application/json;charset=utf8'),
    ('Server', 'nginx/1.0')
]

REQUEST_TIMEOUT = 5
#service port
PORT = 8888

SESSION_SECRET = '3cdcb1f00803b6e78ab50b466a40b9977db396840c28307f428b25e2277f1bcc'
SESSION_TIMEOUT = 180

#excel列宽
EXCEL_DEFAULT_WIDTH = 2960
EXCEL_LARGE_WIDTH = 256 * 20
EXCEL_SMALL_WIDTH = 256 * 10


#股票行情
STOCK_PATCH_HQ_URL = '/batch/stock/price'
STOCK_SINGLE_HQ_URL = '/stock/price'
STOCK_HQ_KEY = 's2q4y3er'
STOCK_CACHE_DIR = r_path + '/www/cache/quote/'
STOCK_ALL_STOCKS_FILE = STOCK_CACHE_DIR + 'stocks.json'


#order_status
ORDER_STATUS = {
    'unsend':'未报',
    'tosend':'待报',
    'sending':'正报',
    'sent':'已报',
    'tocancel':'待撤',
    'canceling':'正撤',
    'canceled':'已撤',
    'pcanceled':'部撤',
    'dealt':'已成',
    'pdealt':'部成',
    'cexpired':'撤废',
    'expired':'废单',
    'pexpired':'部废'
}

# redis configure
REDISCONF = {
    #'host': 'r-2zecb8a8921235a4.redis.rds.aliyuncs.com',
    'host': '127.0.0.1',
    'port': 6379,
    #'password': 'Q7Lt8eksz7Vs2y4g',
    #'password': 'mmzhm123456.',
    'password' : '',
    'database': 5,
    'sock_com': 0,
    'start_pool': True,
}

quote_redis_conf = {
    # "host": 'r-2zecb8a8921235a4.redis.rds.aliyuncs.com',
    "host":'127.0.0.1',
    "port": '6379',
    "db": 14,
    # "pwd": 'Q7Lt8eksz7Vs2y4g',
    "pwd":'',
}

Api={
    "stock":{
        "stock_key":"s2q4y3er",
        "stock":"http://sq.youlikj.com/stock/price",
        "stock_batch":"http://sq.youlikj.com/batch/stock/price",
        "stock_price":r_path + "/www/cache/quote/choice_stocks_hq_data.json",
        "stock_price_yesterday":r_path + "/www/cache/quote/choice_stocks_hq_data_yesterday.json",
        "stock_info":r_path + "/www/cache/quote/stocks.json",
        "trade_dates":r_path + "/www/cache/quote/trade_dates.json",
    },
    "ams":{
        "btype":"dts",
        "key":"dts@oak_2019@AMS-dev",
        "url":"http://fapi.am.youlikj.com",
    }
}

otype_enum = {
    'ptmr':'普通买入',
    'ptmc':'普通卖出',
    'rzmr':'融资买入',
    'mqhk':'卖券还款',
}

hq_key = 's2q4y3er'




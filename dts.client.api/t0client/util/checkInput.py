import re,hashlib
from ..config.config import *
import xlwt
import io
from ..config.pubconf import *
import requests
from ..error import *
from urllib.parse import urlencode
import logging
import time,datetime
from decimal import Decimal
from functools import reduce
from ..util.quote import Quote
from ..error import *


def md5(str):
    m = hashlib.md5()
    m.update(str.encode('utf-8'))
    return m.hexdigest()

def checkPwd(pwd):
    '''校验密码格式'''
    reg_exp_pwd = r'^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{6,20}$'
    if re.match(reg_exp_pwd, pwd) is None:
        return False
    else:
        return True

def getPwd(pwd):
    return md5(pwd + SECRET_KEY).lower()

def getExchangeByCode(code):
    first_str = code[:1]
    if (first_str == '6'):
        return "SH"
    else:
        return "SZ"

def outExcel(name,row_key,row_value,list,width=[]):
    workboot = xlwt.Workbook(encoding='utf-8')
    worksheet = workboot.add_sheet(name)
    list_count = len(list) if list is not None else 0

    #表头
    row0 =row_key
    style0 = xlwt.easyxf('font: bold on;align: wrap on, vert centre, horiz left')
    for i in range(len(row0)):
        worksheet.write(0, i, row0[i],style0)
        if width != []:
            worksheet.col(i).width=width[i]

    #表内容数据
    j = 1
    style1 = xlwt.easyxf('align: wrap on, vert centre, horiz left')
    if list_count > 0:
        for key in range(list_count):
            for row in range(len(row_value)):
                worksheet.write(j, row, list[key][row_value[row]],style1)
            j += 1

    sio = io.BytesIO()
    workboot.save(sio)
    return sio.getvalue()

def getToday():
    return time.strftime("%Y-%m-%d",time.localtime())

def getHqSign(timestamp):
    return md5(str(timestamp)+'&'+STOCK_HQ_KEY)

def batchGetStockHq(code_list_str):
    timestamp = round(time.time())
    params = {'codes':code_list_str,'sign':getHqSign(timestamp),'timestamp':timestamp}
    url = HQ_DOMAIN + STOCK_PATCH_HQ_URL
    logging.info(url + '?' + urlencode(params))
    try:
        res = requests.get(url,params).json()
        return res['data']['list']
    except:
        raise error_api_service_exception

def batchGetStockHqFromFile():
    url = Api['stock']['stock_price']
    import time, json
    for i in range(2):
        with open(url, 'r') as f:
            rt = f.read()
        if rt is not None and rt != '':
            break
        time.sleep(0.1)
    all_price = json.loads(rt)
    stock_price_list = {}
    for stock_info in all_price:
        stock_price_list[stock_info['stock_code']] = stock_info['price']
    return stock_price_list

def batchGetStockHqFromQuote(code_list:list):
    try:
        quote_client = Quote(quote_redis_conf)
        prices = quote_client.get_stock_prices(code_list)
    except Exception as e:
        logging.info(e)
        raise error_hq_service_exception

    if None in prices.values():
        logging.info(prices)
        logging.info('None in prices')
        raise error_hq_data_exception
    return prices

def format_number(number,bit,persent=0):
    number = round(number, bit)
    print(number)
    if persent==1:
        number = str(Decimal(float(number)*100).quantize(Decimal('0.00'))) + '%'
    return number

def getRemarkStr(related_info):
    if isinstance(related_info,str):
        return related_info + ';'

    res_str = ''
    if related_info == []:
        return res_str

    for r in related_info:
        res_str = res_str + ':'.join(r)+'; '
    return res_str

def format_nonevalue(value):
    if value is None:
        return '--'
    else:
        return value

def format_round(number):
    return float(Decimal(float(number)).quantize(Decimal('0.00')))

def getLastExchangeDay(holidays=[],fdate=''):
    """
        获取指定日期的上一个交易日的日期，fdate默认为空，即获取今天的上一个交易日
    """
    if fdate == '':
        now_time = datetime.datetime.now()
    else:
        now_time = datetime.datetime.strptime(fdate+'  00:00:01', "%Y-%m-%d %H:%M:%S")

    yes_date_str = ''
    for i in range(1, 10):
        yes_time = now_time + datetime.timedelta(days=-i)
        yes_date_str = yes_time.strftime('%Y-%m-%d')
        if yes_time.weekday() != 5 and yes_time.weekday() != 6 and yes_date_str not in holidays:
            break
    return yes_date_str

def dateToMillTimstamp(date_str,time_str=''):
    """
        返回给定日期给定时刻的毫秒时间戳，time_str默认为空，即获取给定日期0点的毫秒时间戳
    """
    if time_str == '':
        time_str = '00:00:00'
    date_time_str = date_str + ' ' + time_str
    return int(time.mktime(time.strptime(date_time_str,"%Y-%m-%d %H:%M:%S"))) * 1000

def getTodayStartTimestamp(holidays=[],fdate=''):
    """
        获取"当日"的开始毫秒级时间戳（13位）
    """
    date_str = getLastExchangeDay(holidays,fdate)
    return dateToMillTimstamp(date_str,'15:00:00')

def getuniqlist(data_list):
    run_function = lambda x, y: x if y in x else x + [y]
    return reduce(run_function, [[], ] + data_list)

def checkPrice(price):
    reg_exp = r'^\d+\.\d+$'
    if re.match(reg_exp, str(price)) is None:
        return False
    else:
        return True




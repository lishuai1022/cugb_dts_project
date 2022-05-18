from .checkInput import *
from functools import reduce
import decimal
from ..config.pubconf import *

def getMatchRecord(cnum ,record_arr):
    '''
        获取某个资金账户 某一只股票 的头寸的发生金额
        cnum是头寸数量，带方向，-表示买>卖；+表示买<卖
        record_arr是按委托时间升序排列的list，包括买入卖出的所有记录，不包括虚拟记录
    '''
    if not isinstance(cnum ,int):
        cnum = int(cnum)
    if cnum == 0:
        return 0

    # 根据头寸数量的正负，把数据集过滤成要找的数据集
    res_arr = []
    if cnum < 0  :  # 买>卖
        res_arr = list(filter(lambda record :int(record['dcount'] ) <0 ,record_arr))
    else  :  # 买<卖
        res_arr = list(filter(lambda record :int(record['dcount'] ) >0 ,record_arr))

    # 匹配记录
    totalnum = abs(cnum)  # 总匹配数量的剩余数量，不区分方向，取绝对值
    totalmoney = 0  # 总发生金额，带方向，-表示买>卖；+表示买<卖
    res_arr.reverse(  )  # 从后往前找
    for i in res_arr:
        # print(i)
        dcount = abs(int(i['dcount']))
        if dcount >= totalnum  :  # 记录数量 >= 头寸数量
            totalmoney += float(i['amount']) / dcount * totalnum
            break
        else  :  # 记录数量 < 头寸数量
            totalnum -= dcount
            totalmoney += float(i['amount'])

    return totalmoney


def getVirtualCMoney(arr):
    '''
        批量获取多只股票头寸的虚拟平仓金额
        返回的发生金额带符号，与ccount符号相反
        arr是股票头寸的list
        arr = [
            {
                'ccount':'-200',
                'ccode':'600031',

            },
            {
                'ccount':'100',
                'ccode':'300111',

            }
        ]
    '''

    # 1.批量获取行情数据，得到股票现价
    ccode_list_str = reduce(lambda record1, record2: str(record1['ccode']) + ',' + str(record2['ccode']), arr)
    hq_res = batchGetStockHq(ccode_list_str)

    # 2.取ccount的相反数，乘以现价，得到虚拟平仓金额。不计算手续费等费用
    for c in arr:
        for q in hq_res:
            if c['ccode'] == q['stock_code']:
                c['price'] = q['price']
                c['vpmoney'] = -1 * int(c['ccount']) * q['price']
                c['vpmoney'] = decimal.Decimal(c['vpmoney']).quantize(Decimal('0.00'))
                break

    return arr

def getAllStocks():
    import time, json
    for i in range(2):
        url = STOCK_ALL_STOCKS_FILE
        with open(url, 'r') as f:
            rt = f.read()
        if rt is not None and rt != '':
            break
        time.sleep(0.1)
    stocks = json.loads(rt)
    return stocks




if __name__ == '__main__':
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
    getVirtualCMoney(arr)
#     record_arr = [
#         {
#             "id": 1,
#             "dcount": "-100",
#             "dprice": "2.00",
#             "amount": "-200.00",
#         },
#         {
#             "id": 2,
#             "dcount": "100",
#             "dprice": "2.00",
#             "amount": "200.00",
#         },
#
#         {
#             "id": 3,
#             "dcount": "-100",
#             "dprice": "2.00",
#             "amount": "-200.00",
#         },
#         {
#             "id": 4,
#             "dcount": "-300",
#             "dprice": "2.00",
#             "amount": "-600.00",
#         },
#         {
#             "id": 5,
#             "dcount": "-500",
#             "dprice": "3.00",
#             "amount": "-1500.00",
#         },
#         {
#             "id": 6,
#             "dcount": "100",
#             "dprice": "2.10",
#             "amount": "210.00",
#         },
#         {
#             "id": 7,
#             "dcount": "-100",
#             "dprice": "2.10",
#             "amount": "-210.00",
#         },
#         {
#             "id": 8,
#             "dcount": "400",
#             "dprice": "2.00",
#             "amount": "400.00",
#         },
#         {
#             "id": 9,
#             "dcount": "500",
#             "dprice": "3.00",
#             "amount": "1500.00",
#         },
#     ]
#     cmum = -500
#     print(getMatchRecord(cmum ,record_arr))

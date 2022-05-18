from ... import access, forms
from ...error import *
from ..AuthHandler import AuthHandler
from ...daos.OrderDao import OrderDao
from decimal import Decimal
from ...config import pubconf
from ...util import checkInput
from urllib.parse import quote
import time

class FillHandler(AuthHandler):
    @access.exptproc
    def get(self):
        page = self.get_argument('page', 1)
        pagesize = self.get_argument('pagesize', 10)
        ccode = self.get_argument('ccode', '')
        side = self.get_argument('side', '')
        sdate = self.get_argument('sdate', '')
        edate = self.get_argument('edate', '')
        faccount_id = self.get_argument('faccount_id', '')

        stimestamp = checkInput.dateToMillTimstamp(sdate)  # 开始毫秒时间戳
        etimestamp = checkInput.dateToMillTimstamp(edate, '23:59:59')  # 结束毫秒时间戳

        orderdao = OrderDao()
        total = orderdao.getAllFillListTotal(self.trader_id, faccount_id, ccode, side, stimestamp, etimestamp)
        datalist = orderdao.getAllFillList(self.trader_id, faccount_id, ccode, side, stimestamp, etimestamp, page,
                                           pagesize, False)

        for dt in datalist:
            dt['ddate'] = time.strftime("%Y-%m-%d", time.localtime(dt['dtime'] / 1000))  # 成交日期
            dt['dtime'] = time.strftime("%H:%M:%S", time.localtime(dt['dtime'] / 1000))  # 成交时间

            # dt['stfee'] = dt['stfee'] if dt['stfee'] is not None else 0
            # dt['rfee'] = dt['rfee'] if dt['rfee'] is not None else 0
            # dt['tfee'] = dt['tfee'] if dt['tfee'] is not None else 0
            # dt['fee'] = dt['stfee'] + dt['rfee'] + dt['tfee']  # 交易费用
            # if dt['side'] == 0:
            #     dt['dmoney'] = float(dt['amount']) + float(dt['fee'])
            # else:
            #     dt['dmoney'] = float(dt['amount']) - float(dt['fee'])

            dt['dmoney'] = str(Decimal(dt['amount']).quantize(Decimal('0.00')))
            dt['side'] = '买入' if dt['side'] == 0 else '卖出'  # 委托方向
            dt['dprice'] = str(dt['dprice'])
            dt['amount'] = str(Decimal(float(dt['dprice']) * float(dt['dcount'])).quantize(Decimal('0.00')))
            dt['ocode'] = str(dt['ocode'])
            # dt['type'] = "虚拟委托" if dt['type'] == 1 else '--'
            # dt['fee'] = str(dt['fee'])

        # 导出
        title_list = ["证券代码", "证券名称", "资金账户", "成交日期", "成交时间", "委托方向", "成交价格", "成交数量", "成交金额",
                      "发生金额", "委托编号"]
        field_list = ["ccode", "cname", "fname", "ddate", "dtime", "side", "dprice", "dcount", "amount",
                       "dmoney", "ocode"]
        default_width = pubconf.EXCEL_DEFAULT_WIDTH
        large_width = pubconf.EXCEL_LARGE_WIDTH
        small_width = pubconf.EXCEL_SMALL_WIDTH
        width_list = [default_width, default_width, large_width, default_width, default_width, default_width,
                      default_width, default_width, default_width, default_width, large_width]
        filename = '成交记录.xls'
        sheet_name = '成交记录'
        self.set_header('Content-type', 'application/vnd.ms-excel')
        self.set_header('Content-Disposition', 'attachment;filename=%s' % quote(filename))
        return self.write(checkInput.outExcel(sheet_name, title_list, field_list, datalist, width_list))
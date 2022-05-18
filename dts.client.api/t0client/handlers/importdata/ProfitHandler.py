from ... import access, forms
from ...error import *
from ..AuthHandler import AuthHandler
from ...daos.OrderDao import OrderDao
from ...config import pubconf
from ...util import checkInput
from urllib.parse import quote
from decimal import Decimal

class ProfitHandler(AuthHandler):
    @access.exptproc
    def get(self):
        faccount_id = self.get_argument('faccount_id', '')
        ccode = self.get_argument('ccode', '')
        sdate = self.get_argument('sdate', '')
        edate = self.get_argument('edate', '')
        isnew = self.get_argument('isnew','0')
        source = self.get_argument('source', '0')
        if source not in ['0', '1', '2']:
            source = '0'


        orderdao = OrderDao()
        datalist = orderdao.getTraderProfitList(self.trader_id,faccount_id,ccode,sdate,edate,'','',False,source)

        for dt in datalist:
            dt['odate'] = str(dt['odate'])
            dt['tprofit'] = str(Decimal(dt['tprofit']).quantize(Decimal('0.00')))
            dt['interest'] = str(Decimal(dt['interest']).quantize(Decimal('0.00')))
            dt['profit'] = str(Decimal(dt['profit']).quantize(Decimal('0.00')))
            dt['source'] = '私有券池' if int(dt['source']) == 0 else '公共券池'

        default_width = pubconf.EXCEL_DEFAULT_WIDTH
        large_width = pubconf.EXCEL_LARGE_WIDTH
        small_width = pubconf.EXCEL_SMALL_WIDTH
        if isnew != '' and int(isnew) == 1:  # 新字段顺序
            title_list = ["交易日期", "股票代码", "股票名称", "资金账户", "股票来源","交易盈亏", "融资利息", "已成盈亏"]
            field_list = ["odate", "ccode", "cname", "fname", "source", "tprofit", "interest", "profit"]
            width_list = [default_width, default_width, default_width, large_width, default_width, large_width,
                          large_width, default_width]
        else:
            # 导出
            title_list = ["交易日期", "证券代码", "证券名称", "资金账户", "交易盈亏", "融资利息", "已成盈亏"]
            field_list = ["odate", "ccode", "cname", "fname", "tprofit", "interest", "profit"]
            width_list = [default_width, default_width, default_width, large_width, large_width,
                          large_width, default_width]

        filename = '盈亏报表.xls'
        sheet_name = '盈亏报表'
        self.set_header('Content-type', 'application/vnd.ms-excel')
        self.set_header('Content-Disposition', 'attachment;filename=%s' % quote(filename))
        return self.write(checkInput.outExcel(sheet_name, title_list, field_list, datalist, width_list))
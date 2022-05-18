from ... import access, forms
from ...error import *
from ..AuthHandler import AuthHandler
from ...daos.TQuerydao import *
from ...config import pubconf
from ...util import checkInput
import logging
from decimal import Decimal
from urllib.parse import quote

class PositionHandler(AuthHandler):
    @access.exptproc
    def get(self):
        tquerydao = TQueryDao()
        datalist = tquerydao.getPosition(self.taccount_id)

        if datalist is not None and datalist != ():
            code_list = []
            for d in datalist:
                code_list.append(d['code'])
            code_str = ','.join(code_list)

            hq_data = checkInput.batchGetStockHq(code_str)
            logging.info(hq_data)
            hq_res = {}
            for k in hq_data:
                hq_res[k['stock_code']] = k['price']

            for dt in datalist:
                dt['price'] = hq_res[dt['code']]
                dt['f_hprice'] = str(dt['hprice'].quantize(Decimal('0.00')))
                dt['market_value'] = str(Decimal(dt['price'] * dt['hcount']).quantize(Decimal('0.00')))
                dt['hold_profit'] = str(Decimal((dt['price'] - float(dt['hprice'])) * dt['hcount']).quantize(Decimal('0.00')))
                dt['profit_rate'] = str(Decimal((dt['price'] - float(dt['hprice']))/ float(dt['hprice']) * 100).quantize(Decimal('0.00'))) + '%'



        # 导出
        title_list = ["ID","股票代码", "股票名称", "成本价","现价", "持仓数量", "可用数量","市值","持仓盈亏","盈亏比例"]
        field_list = ["position_id","code", "name", "f_hprice","price", "hcount", "ucount","market_value","hold_profit","profit_rate"]
        default_width = pubconf.EXCEL_DEFAULT_WIDTH
        large_width = pubconf.EXCEL_LARGE_WIDTH
        small_width = pubconf.EXCEL_SMALL_WIDTH
        width_list = [small_width, default_width, default_width, default_width, default_width,default_width,default_width,default_width,default_width,default_width]
        filename = '持仓.xls'
        sheet_name = '持仓'
        self.set_header('Content-type', 'application/vnd.ms-excel')
        self.set_header('accept-language', 'zh-cn')
        self.set_header('Content-Disposition', 'attachment;filename=%s' % quote(filename))
        return self.write(checkInput.outExcel(sheet_name, title_list, field_list, datalist, width_list))

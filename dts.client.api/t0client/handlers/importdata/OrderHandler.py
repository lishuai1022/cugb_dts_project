from ... import access, forms
from ...error import *
from ..AuthHandler import AuthHandler
from ...daos.OrderDao import OrderDao
from decimal import Decimal
from ...config import pubconf
from ...util import checkInput
from urllib.parse import quote
import time,json

class OrderHandler(AuthHandler):
    @access.exptproc
    def get(self):
        faccount_id = self.get_argument('faccount_id', '')
        ccode = self.get_argument('ccode', '')
        side = self.get_argument('side', '')
        sdate = self.get_argument('sdate', '')
        edate = self.get_argument('edate', '')
        isnew = self.get_argument('isnew','0')
        source = self.get_argument('source', '0')
        if source not in ['0', '1', '2']:
            source = '0'

        orderdao = OrderDao()
        datalist = orderdao.getAllOrderList(self.trader_id,faccount_id,ccode,side,sdate,edate,'','',False,source)
        for dt in datalist:
            dprice = dt['dprice'] if dt['dprice'] is not None else 0.00
            dcount = dt['dcount'] if dt['dcount'] is not None else 0

            dt['dmoney'] = str(Decimal(dprice * dcount).quantize(Decimal('0.00')))
            dt['odate'] = str(dt['odate'])
            dt['otime2'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(dt['otime']/1000))
            dt['otime'] = time.strftime("%H:%M:%S",time.localtime(dt['otime']/1000))
            dt['dtime'] = '--' if dt['dtime'] is None else time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(dt['dtime']/1000))
            dt['side'] = '买入' if dt['side']==0 else '卖出'
            dt['status'] = pubconf.ORDER_STATUS[dt['status']]
            dt['oprice'] = str(dt['oprice'])
            dt['dprice'] = str(dt['dprice']) if dt['dprice'] is not None else '--'
            dt['dcount'] = str(dt['dcount']) if dt['dcount'] is not None else '--'
            dt['dmoney'] = str(dt['dmoney']) if dt['dmoney'] !=0.00 else '--'
            dt['type'] = "虚拟委托" if dt['type']==1 else '--'
            dt['amount'] = str(dt['amount'])
            dt['cost'] = str(dt['cost'])
            dt['source'] = '私有券池' if int(dt['source']) == 0 else '公共券池'
            dt['otype'] = pubconf.otype_enum[dt['otype']]
            try:
                import json
                costs_tmp = json.loads(dt['costs'])
                costs_list = []
                for s in costs_tmp:
                    s[1] = Decimal(s[1]).quantize(Decimal('0.00'))
                    costs_list.append(s[0] + ':' + str(s[1]))
                costs_str = ','.join(costs_list)
                dt['costs'] = costs_str
            except:
                # print('eeeeeee')
                pass
        default_width = pubconf.EXCEL_DEFAULT_WIDTH
        large_width = pubconf.EXCEL_LARGE_WIDTH
        small_width = pubconf.EXCEL_SMALL_WIDTH
        if isnew != '' and int(isnew) == 1: #新字段顺序
            title_list = ['股票代码','股票名称','资金账户','股票来源','委托编号','委托方向','状态','买卖方式','委托价格','委托数量','成交价格','成交数量','成交金额','交易费用','发生金额','委托时间','成交时间','备注']
            field_list = ['ccode', 'cname', 'fname','source','ocode','side','status','otype','oprice','ocount','dprice','dcount','dmoney','cost','amount','otime2','dtime','type']

            width_list = [default_width, default_width, default_width,default_width,large_width, default_width, default_width, default_width,default_width,
                          default_width, default_width, default_width, default_width, default_width, default_width,
                          large_width, large_width, large_width]
        else:
            # 导出
            title_list = ["证券代码","证券名称","资金账户","委托日期","委托时间","委托方向","委托状态","委托价格","委托数量","成交价格","成交数量","成交金额","交易费用","费用明细","发生金额","委托编号","备注"]
            field_list = ["ccode", "cname", "fname", "odate","otime","side","status","oprice","ocount","dprice","dcount","dmoney","cost","costs","amount","ocode","type"]
            width_list = [default_width, default_width, large_width, default_width, default_width,  default_width, default_width, default_width, default_width, default_width, default_width, default_width, default_width,large_width, default_width, large_width,default_width]
        filename = '委托记录.xls'
        sheet_name = '委托记录'
        self.set_header('Content-type', 'application/vnd.ms-excel')
        self.set_header('Content-Disposition', 'attachment;filename=%s' % quote(filename))
        return self.write(checkInput.outExcel(sheet_name, title_list, field_list, datalist, width_list))
"""
    error definition
"""
from . import protocol


class ProcessError(Exception):
    def __init__(self, status, msg):
        self._status = status
        self._msg = msg

    @property
    def status(self):
        return self._status

    @property
    def msg(self):
        return self._msg

    @property
    def data(self):
        return protocol.failed(self._status, self._msg)

    def __str__(self):
        return 'status: '+str(self._status)+', msg: '+self._msg

#---------------------------------------------------------------------
error_common_exception = ProcessError('-2001','服务异常，请稍后重试')
missing_common_params = ProcessError('-2002','缺少公共参数！')
#参数
missing_parameters = ProcessError('-2101', '缺少参数')
invalid_parameters = ProcessError('-2102', '参数错误')
invalid_access = ProcessError('-2103', '账号未登录')
token_error = ProcessError('-2104', 'token验证失败')
quantity_error = ProcessError('-2105', '委托买入数量应为100的倍数')
price_error = ProcessError('-2106','委托价格格式不正确')

#验证码：
error_imgcode_valid_exception = ProcessError('-2301','验证码不正确')
error_imgcode_expire_exception = ProcessError('-2302','验证码已过期')


#修改密码
error_pwd_format_exception = ProcessError('-2501','账号或密码格式不正确')
error_pwd_valid_exception = ProcessError('-2502','账号或密码不正确')
error_account_exception = ProcessError('-2503','该账户目前停用，暂时无法登录操作！')

#api访问
error_api_service_exception = ProcessError('-2601','接口服务错误')
error_api_data_exception = ProcessError('-2602','接口服务忙，请稍后重试')
error_api_data_error = ProcessError('-2603','数据错误[账户不存在，或未开通交易功能]')


#风控信息
risk_blimit_error = ProcessError('-2701','您的账户处于锁开仓，不允许开仓操作！')
risk_bslimit_error = ProcessError('-2702','您的账户处于锁开平仓，暂时无法交易！')
risk_disable_error = ProcessError('-2703','您的账户处于停用中，暂时无法交易！')
risk_max_money = ProcessError('-2704','超出单笔最大下单金额')
risk_max_count = ProcessError('-2705','超出单笔最大委托数量')
risk_single_max_credit = ProcessError('-2706','该股票已超最大头寸，不允许开仓操作！')
risk_sum_max_credit = ProcessError('-2707','账户头寸已超累计最大头寸，不允许开仓操作！')
risk_single_max_loss = ProcessError('-2708','该股票亏损已超亏损预警金额，不允许开仓操作！')
risk_sum_max_loss = ProcessError('-2709','账户亏损已超累计亏损预警金额，不允许开仓操作！')
risk_trade_date = ProcessError('-2710','当前不是交易日')
risk_trade_time = ProcessError('-2711','请在交易时间段操作')

risk_single_max_credit_quantity = ProcessError('-2712','平仓时下单数量不能大于头寸数量！')

#交易操作
trd_no_valid_order = ProcessError('-2801','没有可撤的订单')
trd_no_enough_money = ProcessError('-2802','可用余额不足')
trd_no_enough_count = ProcessError('-2803','可用数量不足')
trd_database_error = ProcessError('-2804','订单入库失败')
trd_quantity_buy_error = ProcessError('-2805','超出最大可买数量')
trd_quantity_sell_error = ProcessError('-2806','超出最大可卖数量')
trd_no_position_error = ProcessError('-2807','没有分配该股票或没有持仓')
trd_no_public_access_error = ProcessError('-2808','没有访问公共券池的权限')


error_hq_service_exception = ProcessError('-2694','行情服务异常')
error_hq_data_exception = ProcessError('-2695','行情数据错误')
"""
    public Trade config
"""

#单张手续费低价code
CODE_UNIT_FEE="50etf_unitfee"

#限价委托最大最小张数code
CODE_MAX_BUY_COUNT="50etf_max_buy_xj"
CODE_Min_BUY_COUNT="50etf_min_buy_xj"

#交易的委托状态类型
#tosend-待报，sent-已报，tocancel-待撤, canceling-正撤，canceled-已撤，pcanceled-部撤，dealt-已成，pdealt-部成, expired-过期
ENTRUST_STATUS_TOSENT="tosend"
ENTRUST_STATUS_SENT="sent"
ENTRUST_STATUS_TOCANCEL="tocancel"
ENTRUST_STATUS_CANCELING="canceling"
ENTRUST_STATUS_CANCELED="canceled"
ENTRUST_STATUS_PCANCELED="pcanceled"
ENTRUST_STATUS_DEALT="dealt"
ENTRUST_STATUS_PDEALT="pdealt"
ENTRUST_STATUS_EXPIRED="expired"

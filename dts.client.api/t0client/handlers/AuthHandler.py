#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from .. import handler, util, rds
# from .. import models
import logging
from ..models.ApiModel import *
from ..config.config import *
from .. import access
# from ..error import *
from ..daos.TraderDao import *
from ..util import checkInput

class AuthHandler(handler.Handler):
    @access.exptproc
    def prepare(self):
        trader_id = self.get_argument('trader_id', '')
        token = self.get_argument('token', '')
        if trader_id == '' or token == '':
            version = self.get_argument('_v','')
            if version == '2':
                raise missing_common_params
            else:
                raise missing_parameters

        key = self.getUserTokenKey(trader_id)
        user_token = self.redis.get(key)
        if user_token is None:
            raise invalid_access

        if user_token != token:
            raise token_error

        self.trader_id = trader_id
        self.client_token = token
        traderDao = TraderDao()
        traderinfo = traderDao.getTraderAccount(trader_id)
        self.traderinfo = traderinfo
        self.account = traderinfo['account']
        # self.taccount_id = traderinfo['taccount_id']
        # self.apiModel = ApiModel()
        # self.traderapi_hash = TRADE_REDIS_HASH

    def importres(self,filename,title_list,sheet_name,field_list):
        self.set_header('Content-type', 'application/vnd.ms-excel')
        self.set_header('Content-Disposition', 'attachment;filename="%s"'%(filename))
        title_list = ["交易账户ID", "交易账户名称", "总资产", "股票市值", "可用金额", "冻结金额", "买入策略", "卖出策略", "预警金额", "平仓金额", "交易账户状态"]
        name = "交易账户"
        row_value = ["taccount_id", "name", "assets", "market_value", "lmoney", "fmoney", "buying_strategy",
                     "selling_strategy", "wmoney", "pmoney", "status"]
        return self.write(checkInput.outExcel(sheet_name, title_list, field_list, rds))







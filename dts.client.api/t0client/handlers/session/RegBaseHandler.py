#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
注册登录找回密码的基类控制器
'''
from __future__ import with_statement

import tornado.web
from ...config import *
from ...util import session
# from util.log import *
# from util import session
# from models.agent.AgentModel import *


class RegBaseHandler(tornado.web.RequestHandler):

    def initialize(self):
        super(RegBaseHandler, self).initialize()
        self.redis = self.application.redis
        self.session = session.Session(self.application.session_manager, self)

        # app_code = self.get_argument('app_code', 'pz')
        # agent_code = self.get_argument('agent', '')

        # agent = None
        # if agent_code is not None or agent_code != '':
        #     agentModel = AgentModel()
        #     agent = agentModel.getFullByCode(agent_code)
        #
        # if agent is None:
        #     agent = {
        #         'agent_id': '',
        #         'code': '',
        #         'type': ''
        #     }

        # self.agent = agent
        # self.app_code = app_code
        # self.agent_code = agent['code']
        # self.agent_id = agent['agent_id']
        # self.agent_type = agent['type']

    # def getUserTokenKey(self, user_id):
    #     if self.app_code == 'qq':
    #         return 'qq_user_token_' + str(self.agent_code) + '_' + str(user_id)
    #
    #     return 'user_token_' + str(self.agent_code) + '_' + str(user_id)

    def prepare(self):
        # return
        session_id = self.get_argument('session_id', '')

        if self.request.path not in ("/session/id", "/index/agentname", "/login"):
            if session_id == '' or len(session_id) != 64:
                data = {
                    'status': 1004,
                    'msg': 'sess验证失败'
                }
                print(data)
                self.respond_data(data)
                return

    def on_finish(self):
        pass

    def respond_data(self, data):
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.write(data)
        self.finish()

    def md5(self, str):
        import hashlib
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()
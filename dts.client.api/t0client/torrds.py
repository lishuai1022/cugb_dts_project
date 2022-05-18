#!/usr/bin/python
#-*- coding:utf-8 -*-

import tornado.gen
import tornadoredis


from . import config

class TorRedisClient():

    def __init__(self, start_pool = config.REDISCONF['start_pool']):
        if config.REDISCONF['sock_com'] == 1:
            self.redis = tornadoredis.Client(unix_socket_path='/dev/shm/redis.sock',db=config.REDISCONF['database'])
            return

        if start_pool == False:
            self.redis = tornadoredis.Client(
                host=config.REDISCONF['host'],
                port=config.REDISCONF['port'],
                selected_db=config.REDISCONF['database'], 
                password=config.REDISCONF['password']
            )
        else:
            self.pool = tornadoredis.Client(
                max_connections = 10,
                host=config.REDISCONF['host'],
                port=config.REDISCONF['port'],
                selected_db=config.REDISCONF['database'], 
                password=config.REDISCONF['password']
            )
            self.redis = tornadoredis.Client(connection_pool=self.pool, socket_timeout=120)

    def get_client(self):
        return self.redis



if __name__ == '__main__':

    pass
#!/usr/bin/python
#-*- coding:utf-8 -*-

import redis
from redis.sentinel import Sentinel

from .config import pubconf as config

class RedisClient():

    def __init__(self, start_pool = config.REDISCONF['start_pool']):
        if config.REDISCONF['sock_com'] == 1:
            self.redis = redis.StrictRedis(unix_socket_path='/dev/shm/redis.sock',db=config.REDISCONF['database'])
            return

        if start_pool == False:
            self.redis = redis.StrictRedis(
                host=config.REDISCONF['host'],
                port=config.REDISCONF['port'],
                db=config.REDISCONF['database'], 
                password=config.REDISCONF['password']
            )
        else:
            self.pool = redis.ConnectionPool(
                max_connections = 5,
                host=config.REDISCONF['host'],
                port=config.REDISCONF['port'],
                db=config.REDISCONF['database'], 
                password=config.REDISCONF['password'],
                socket_keepalive = True
            )
            self.redis = redis.StrictRedis(connection_pool=self.pool, socket_timeout=120)

    def getMaster(self):
        return self.redis

    def startPipeline(self):
        pipeline = self.redis.pipeline(True)
        return pipeline

    def execPipeline(self, pipeline):
        return pipeline.execute()


    def set(self, key, val, ex=None, px=None, nx=False, xx=False):
        return self.redis.set(key, val, ex, px, nx, xx)

    def setex(self, key, time, value):
        return self.redis.setex(key, time, value)

    def setnx(self, key, value):
        return self.redis.setnx(key, value)

    def get(self,key):
        val =  self.redis.get(key)
        if val is not None:
            return str(val,encoding='utf-8')

    def delete(self, key):
        return self.redis.delete(key)

    def rpush(self, list, val):
        self.redis.rpush(list, val)

    def incr(self,key):
        return self.redis.incr(key)

    def transaction(self,func, key):
        return self.redis.transaction(func, key)


    def cacheZset(self, key, kwargs, timeout = 10):
        pipeline = self.startPipeline()
        pipeline.zadd(key, **kwargs)
        pipeline.expire(key, timeout)
        return self.execPipeline(pipeline)

    def hset(self,name, key, value):
        return self.redis.hset(name, key, value)

    def hmget(self,name, *args):
        return self.redis.hmget(name, *args)

    def hget(self,name, key):
        return self.redis.hget(name, key)

    def hdel(self,name, key):
        return self.redis.hdel(name, key)

    def hincrby(self,name, key, value):
        return self.redis.hincrby(name, key, value)

    def zadd(self, name, *args, **kwargs):
        return self.redis.zadd(name, *args, **kwargs)

    def incr(self, key):
        return self.redis.incr(key)

    def pubsub(self):
        return self.redis.pubsub()

    def publish(self, chan, val):
        return self.redis.publish(chan, val)


        
rds_cli = RedisClient()
if __name__ == '__main__':

    pass
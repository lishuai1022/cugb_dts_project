#!/usr/bin/env python
# -*- coding: utf-8 -*-
import redis


class RedisClient():
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, host, port, pwd=None, db=14, max_connections=3):
        if '_conn' not in self.__dict__:
            connection_pool = redis.ConnectionPool(
                host=host,
                port=port,
                password=pwd,
                db=db,
                max_connections=max_connections
            )

            self._conn = redis.StrictRedis(connection_pool=connection_pool)

    def start_pipeline(self):
        pipeline = self._conn.pipeline(False)
        return pipeline

    def exec_pipeline(self, pipeline):
        return pipeline.execute()

    def hset(self, name, key, value):
        return self._conn.hset(name, key, value)

    def hget(self, name, key):
        return self._conn.hget(name, key)


class Quote():
    def __init__(self, redis_conf):
        self._redis = RedisClient(**redis_conf)

    def get_stock_prices(self, codes):
        _pipeline = self._redis.start_pipeline()
        for code in codes:
            _pipeline.hget('stock_tick_' + code, 'price')

        result = self._redis.exec_pipeline(_pipeline)

        prices = {}
        for i, code in enumerate(codes):
            prices[code] = result[i]
            if prices[code] is not None:
                prices[code] = str(prices[code], encoding='utf-8')
        return prices


if __name__ == "__main__":
    redis_conf = {
        # "host": '10.0.1.155',
        # "host": 'r-2zecb8a8921235a4.redis.rds.aliyuncs.com',
        "host": '127.0.0.1',
        "port": '6379',
        "db": 14,
        # "pwd": 'Q7Lt8eksz7Vs2y4g',
        "pwd":''
    }
    quote_client = Quote(redis_conf)
    prices = quote_client.get_stock_prices(['000001','000002'])
    print(prices)
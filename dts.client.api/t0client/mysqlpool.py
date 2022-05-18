#!/usr/bin/python
# -*- coding:utf-8 -*-

import pymysql
from pymysql.cursors import DictCursor
from DBUtils.PooledDB import PooledDB

from . import config


class MysqlPool(object):
    """
        MYSQL数据库对象，负责产生数据库连接, 此类中的连接采用连接池实现
    """

    def __init__(self, cfg=config.DATABASES['peizi']):
        self.__getPool(cfg)

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'inst'):
            cls.inst = super().__new__(cls, *args, **kwargs)
        return cls.inst

    def __getPool(self, cfg):
        """
        @summary: 静态方法，从连接池中取出连接
        """
        print("get mysql pool")
        if not hasattr(self, "_pool"):
            print('create mysql pool')
            self._pool = PooledDB(
                creator=pymysql,
                mincached=1,
                maxcached=10,
                maxconnections=20,
                maxusage=5000,
                host=cfg['host'],
                port=cfg['port'],
                user=cfg['user'],
                passwd=cfg['password'],
                db=cfg['database'],
                use_unicode=True,
                charset=cfg['charset'],
                connect_timeout=5,
                read_timeout=5,
                write_timeout=5,
                cursorclass=DictCursor
            )
        return self._pool

    # 从连接池中取出一个连接
    def __getConn(self):
        conn = self._pool.connection()
        cursor = conn.cursor()
        return cursor, conn

    def close(self, cursor, conn):
        cursor.close()
        conn.close()

    def escape(self, text):
        return pymysql.escape_string(text)

    def execute_fetchall(self, sqlstr, params=[]):
        try:
            _cursor, _conn = self.__getConn()
            if len(params) == 0:
                _cursor.execute(sqlstr)
            else:
                _cursor.execute(sqlstr, params)
            return _cursor.fetchall()
        except Exception as e:
            print(e)
            return []
        finally:
            self.close(_cursor, _conn)

    def execute(self, sqlstr, params=[]):
        try:
            _cursor, _conn = self.__getConn()
            if len(params) == 0:
                effect_row = _cursor.execute(sqlstr)
            else:
                effect_row = _cursor.execute(sqlstr, params)

            _conn.commit()
            return effect_row
        except Exception as e:
            print(e)
            return -1
        finally:
            self.close(_cursor, _conn)

    def execute_fetchone(self, sqlstr, params=[]):
        try:
            _cursor, _conn = self.__getConn()
            if len(params) == 0:
                _cursor.execute(sqlstr)
            else:
                _cursor.execute(sqlstr, params)
            return _cursor.fetchone()
        except Exception as e:
            print(e)
            return None
        finally:
            self.close(_cursor, _conn)

    def execute_commit(self, sqlstr, params=[]):
        try:
            _cursor, _conn = self.__getConn()
            if len(params) == 0:
                _cursor.execute(sqlstr)
            else:
                _cursor.execute(sqlstr, params)
            insert_id = self.__getInsertId(_cursor)
            _conn.commit()
            return insert_id
        except Exception as e:
            print(e)
            return []
        finally:
            self.close(_cursor, _conn)

    def executemany_commit(self, sqlstr, values):
        try:
            _cursor, _conn = self.__getConn()
            _cursor.executemany(sqlstr, values)
            _conn.commit()
        except Exception as e:
            print(e)
            return
        finally:
            self.close(_cursor, _conn)

    def __getInsertId(self, cursor):
        """
        获取当前连接最后一次插入操作生成的id,如果没有则为0
        """
        cursor.execute("SELECT @@IDENTITY AS id")
        result = cursor.fetchall()
        if len(result) > 0:
            return result[0]['id']
        return 0

    """
     事务操作
    """

    def trans_fetchone(self, cursor, sqlstr, params=[]):
        if len(params) == 0:
            cursor.execute(sqlstr)
        else:
            cursor.execute(sqlstr, params)
        return cursor.fetchone()

    def execute_nocommit(self, cursor, sqlstr, params=[]):
        if len(params) == 0:
            cursor.execute(sqlstr)
        else:
            cursor.execute(sqlstr, params)
        return cursor.rowcount

    def executemany_nocommit(self, cursor, sqlstr, params=[]):
        return cursor.executemany(sqlstr, params)

    def insert_nocommit(self, cursor, sqlstr, params=[], need_effect_row=False):
        if len(params) == 0:
            cursor.execute(sqlstr)
        else:
            cursor.execute(sqlstr, params)

        if need_effect_row == True:
            return self.__getInsertId(cursor), cursor.rowcount
        else:
            return self.__getInsertId(cursor)

    def end(self, conn, cursor, option='commit'):
        """
        @summary: 结束事务
        """
        if option == 'commit':
            conn.commit()
        else:
            conn.rollback()
        self.close(cursor, conn)

    def begin(self):
        """
        @summary: 开启事务
        """
        _cursor, _conn = self.__getConn()

        _conn.begin()

        return _conn, _cursor


db = MysqlPool()




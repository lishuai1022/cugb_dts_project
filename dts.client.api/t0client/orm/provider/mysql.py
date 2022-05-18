"""
    mysql class
"""
from . import base
from .. import db
import pymysql


class DBMysql(base.Db):
    def __init__(self, **cfg):
        """
            init mysql db with configure

        """
        # database configure
        self._cfg = cfg

        # database object
        self._conn = None

    def connect(self):
        """
            connect to database
        :param config:
        :return:
        """
        if self._conn is None:
            self._conn = pymysql.connect(**self._cfg, cursorclass = pymysql.cursors.DictCursor)

    def close(self):
        """
            close connection to database
        :return:
        """
        if self._conn is not None:
            self._conn.close()
            self._conn = None


    def begin(self):
        """
            begin transaction
        :return:
        """
        # connect
        self.connect()

        # begin transaction
        self._conn.begin()

    def commit(self):
        """
            commit changes to database
        :return:
        """
        if self._conn is not None:
            self._conn.commit()

    def rollback(self):
        """
            rollback transaction
        :return:
        """
        if self._conn is not None:
            self._conn.rollback()

    def execute(self, sql, args=None):
        """

        :param sql:
        :param args:
        :return:
        """
        # connect to database
        self.connect()

        # create cursor
        cursor = self._conn.cursor()

        # execute sql
        affects = cursor.execute(sql, args)

        # rows
        rows = cursor.fetchall()

        return affects, rows

    def select(self, sql, args=None):
        """
            select data
        :param sql:
        :param args:
        :return:
        """
        affects, rows = self.execute(sql, args)
        return rows

    def insert(self, sql, args=None):
        """

        :param sql:
        :param args:
        :return:
        """
        affects, rows = self.execute(sql, args)
        return affects

    def update(self, sql, args=None):
        """

        :param sql:
        :param args:
        :return:
        """
        affects, rows = self.execute(sql, args)
        return affects

    def delete(self, sql, args=None):
        """

        :param sql:
        :param args:
        :return:
        """
        affects, rows = self.execute(sql, args)
        return affects

    def lastrowid(self):
        """
            get last insert primary key id
        :return:
        """
        return self._conn.insert_id()


# register provider
db.register('mysql', DBMysql)
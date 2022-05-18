"""
    base class for database provider
"""


class Db:
    def connect(self):
        """
            connect to database
        :return:
        """
        pass

    def close(self):
        """
            close connection to database
        :return:
        """
        pass

    def begin(self):
        """
            begin transaction
        :return:
        """
        pass

    def commit(self):
        """
            commit changes to database
        :return:
        """
        pass

    def rollback(self):
        """
            rollback transaction
        :return:
        """
        pass

    def select(self, sql, args=None):
        """

        :param sql:
        :return:
        """
        pass

    def insert(self, sql, args=None):
        """

        :param sql:
        :param args:
        :return:
        """
        pass

    def update(self, sql, args=None):
        """

        :param sql:
        :param args:
        :return:
        """
        pass

    def delete(self, sql, args=None):
        """

        :param sql:
        :param args:
        :return:
        """
        pass

    def lastrowid(self):
        """
            last insert row id
        :return:
        """
        pass
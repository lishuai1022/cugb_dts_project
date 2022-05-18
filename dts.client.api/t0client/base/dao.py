"""
    data access object base class
"""


class _Transaction:
    """
        db transaction for model
    """
    def __init__(self, model):
        """
            init a transaction with db
        :param db:
        """
        self._model = model

    def __enter__(self):
        """
            begin transaction
        :return:
        """
        self._model.begin_transaction()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
            end transaction
        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        if exc_val is None:
            self._model.commit_transaction()
        else:
            self._model.rollback_transaction()


class Dao:
    def __init__(self, db):
        """
            init model
        """
        self._db = db

    def transaction(self):
        """
            get transaction of current model
        :return:
        """
        return _Transaction(self)


    def begin_transaction(self):
        """
            begin transaction
        :return:
        """
        self._db.begin()

    def commit_transaction(self):
        """
            commit changes
        :return:
        """
        self._db.commit()

    def rollback_transaction(self):
        """
            rollback transaction
        :return:
        """
        self._db.rollback()

    def execute(self, sql, args=None):
        """
            execute
        :param query:
        :param args:
        :return:
        """
        return self._db.execute(sql, args)

    def insert(self, sql, args=None):
        """
            execute
        :param query:
        :param args:
        :return:
        """
        self._db.execute(sql, args)
        return self._db.last_row_id()

    def update(self, sql, args=None):
        """
            execute
        :param query:
        :param args:
        :return:
        """
        return self._db.execute(sql, args)

    def commit(self):
        """
            commit changes
        :return:
        """
        self._db.commit()

    def select_one(self, sql, args=None):
        """
            select
        :param query:
        :param args:
        :return:
        """
        return self._db.selectone(sql, args)

    def select_all(self, sql, args=None):
        """
            select
        :param query:
        :param args:
        :return:
        """
        return self._db.selectall(sql, args)

    def insert_and_commit(self, sql, args=None):
        """
            execute
        :param query:
        :param args:
        :return:
        """
        self._db.execute(sql, args)
        self._db.commit()
        return self._db.lastrowid()

    def update_and_commit(self, sql, args=None):
        """
            execute
        :param query:
        :param args:
        :return:
        """
        n = self._db.execute(sql, args)
        self._db.commit()
        return n
        
    def last_row_id(self):
        """
            get last insert row id
        :return:
        """
        return self._db.last_row_id()
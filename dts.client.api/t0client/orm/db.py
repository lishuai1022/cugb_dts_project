"""
    database
"""


class DBError(Exception):
    pass


class _Connection:
    """
        database connection
    """
    def __init__(self, db):
        """
            init a connection with db
        :param db:
        """
        self._db = db

    def __enter__(self):
        """
            build connection
        :return:
        """
        self._db.connect()
        return self._db

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
            close connection
        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        self._db.close()


class _Transaction:
    """
        database transaction
    """
    def __init__(self, db):
        """
            init a transaction with db
        :param db:
        """
        self._db = db

    def __enter__(self):
        """
            begin transaction
        :return:
        """
        self._db.connect()

        self._db.begin()
        return self._db

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
            end transaction
        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        if exc_val is None:
            self._db.commit()
        else:
            self._db.rollback()

        self._db.close()


# providers, name->cls
_providers = {}
# databases, alias->[provider, configure(dict)]
_databases = {}


def register(provider, cls):
    """
        register a provider
    :param provider: str, provider name
    :param cls: class, provider class
    :return:
    """
    _providers[provider] = cls


def setup(alias, provider, **cfg):
    """
        setup a new database configure
    :param alias: str, database alias name
    :param cfg: dict, database configure
    :return:
    """
    if provider not in _providers.keys():
        raise DBError('provider %s not support.')
    _databases[alias] = [provider, cfg]


def create(alias=None):
    """
        create a new connection to database with name alias, no transaction
    :param alias:
    :return:
    """
    if len(_databases) == 0:
        raise DBError('none database has setup.')

    if alias is None:
        database = list(_databases.values())[0]
    else:
        database = _databases.get(alias)

    if database is None:
        raise DBError('database %s has not setup.' % str(alias))

    return _Connection(_providers[database[0]](**database[1]))


def atomic(alias=None):
    """
        create a new connection to database with name alias with transaction
    :param alias:
    :return:
    """
    if len(_databases) == 0:
        raise DBError('none database has setup.')

    if alias is None:
        database = list(_databases.values())[0]
    else:
        database = _databases.get(alias)

    if database is None:
        raise DBError('database %s has not setup.' % str(alias))

    return _Transaction(_providers[database[0]](**database[1]))

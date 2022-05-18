"""
    query for database
"""
import copy


class SQLError(Exception):
    """
        sql helper error
    """
    pass


class _Node:
    """
    A single internal node in the tree graph. A Node should be viewed as a
    connection (the root) with the children being either leaf nodes or other
    Node instances.
    """
    # Standard connector type. Clients usually won't use this at all and
    # subclasses will usually override the value.
    default = 'DEFAULT'

    def __init__(self, children=None, connector=None, negated=False):
        """Construct a new Node. If no connector is given, use the default."""
        self.children = children[:] if children else []
        self.connector = connector or self.default
        self.negated = negated

    # Required because django.db.models.query_utils.Q. Q. __init__() is
    # problematic, but it is a natural Node subclass in all other respects.
    @classmethod
    def _new_instance(cls, children=None, connector=None, negated=False):
        obj = _Node(children, connector, negated)
        obj.__class__ = cls
        return obj

    def __str__(self):
        template = '(NOT (%s: %s))' if self.negated else '(%s: %s)'
        return template % (self.connector, ', '.join(str(c) for c in self.children))

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self)

    def __deepcopy__(self):
        obj = _Node(connector=self.connector, negated=self.negated)
        obj.__class__ = self.__class__
        obj.children = copy.deepcopy(self.children)
        return obj

    def __len__(self):
        """Return the the number of children this node has."""
        return len(self.children)

    def __bool__(self):
        """Return whether or not this node has children."""
        return bool(self.children)

    def __contains__(self, other):
        """Return True if 'other' is a direct child of this instance."""
        return other in self.children

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        if (self.connector, self.negated) == (other.connector, other.negated):
            return self.children == other.children
        return False

    def __hash__(self):
        return hash((self.__class__, self.connector, self.negated) + tuple(self.children))

    def add(self, data, conn_type, squash=True):
        if data in self.children:
            return data
        if not squash:
            self.children.append(data)
            return data
        if self.connector == conn_type:
            # We can reuse self.children to append or squash the node other.
            if (isinstance(data, _Node) and not data.negated and
                    (data.connector == conn_type or len(data) == 1)):
                self.children.extend(data.children)
                return self
            else:
                # We could use perhaps additional logic here to see if some
                # children could be used for pushdown here.
                self.children.append(data)
                return data
        else:
            obj = self._new_instance(self.children, self.connector,
                                     self.negated)
            self.connector = conn_type
            self.children = [obj, data]
            return data

    def negate(self):
        """Negate the sense of the root connector."""
        self.negated = not self.negated


class _Query(_Node):
    # Connection types
    AND = 'and'
    OR = 'or'
    default = AND

    def __init__(self, *args, **kwargs):
        connector = kwargs.pop('_connector', None)
        negated = kwargs.pop('_negated', False)

        # process in clause
        for k, v in kwargs.items():
            if k.endswith('__in') and isinstance(v, str):
                kwargs[k] = v.split(',')

        super().__init__(children=list(args) + sorted(kwargs.items()), connector=connector, negated=negated)

    def _combine(self, other, conn):
        if not isinstance(other, Q):
            raise TypeError(other)

        if not other:
            return copy.deepcopy(self)
        elif not self:
            return copy.deepcopy(other)

        obj = type(self)()
        obj.connector = conn
        obj.add(self, conn)
        obj.add(other, conn)
        return obj

    def __or__(self, other):
        return self._combine(other, self.OR)

    def __and__(self, other):
        return self._combine(other, self.AND)

    def __invert__(self):
        obj = type(self)()
        obj.add(self, self.AND)
        obj.negate()
        return obj

    def sql(self):
        """
            generate prepared sql
        :return:
        """
        childs = []
        for child in self.children:
            if isinstance(child, self.__class__):
                template = 'not (%s)' if self.negated else '(%s)'
                childs.append(template % child.sql())
            else:
                childs.append(Q.tpl(child[0], child[1]))

        sep = ' not %s ' % self.connector if self.negated else ' %s ' % self.connector
        return sep.join(childs)

    def args(self):
        """
            generate prepared args
        :return:
        """
        childs = []
        for child in self.children:
            if isinstance(child, self.__class__):
                childs.extend(child.args())
            else:
                if isinstance(child[1], tuple) or isinstance(child[1], list):
                    childs.extend(child[1])
                else:
                    childs.append(child[1])

        return childs

    @staticmethod
    def tpl(cname, cvalue):
        """
            generate sql template by conditon name
        :return:
        """
        # operation compare definition
        OP_CMP = {
            'eq': '`%s`=%s',
            'lt': '`%s`<%s',
            'le': '`%s`<=%s',
            'gt': '`%s`>%s',
            'ge': '`%s`>=%s',
            'ne': '`%s`!=%s'
        }

        # operation in definition
        OP_IN = {
            'in': '`%s` in (%s)'
        }

        # operation like definition
        OP_LIKE = {
            'startswith': '`%s` like \'%s%%\'',
            'endswith': '`%s` like \'%%%s\'',
            'contains': '`%s` like \'%%%s%%\''
        }

        # operation is/is not null definition
        OP_NULL = {
            'null': {
                True: 'is null',
                False: 'is not null'
            }
        }

        # parse name
        items = cname.split('__')
        nitems = len(items)

        # check parse results
        if nitems == 0 or nitems > 2:
            raise SQLError('条件格式错误：%s' % cname)

        # parse condition
        if nitems == 1:
            name = items[0]
            return '%s=%s' % (name, '%s')
        elif nitems == 2:
            name, op = items[0], items[1]

            if op in list(OP_CMP.keys()):
                return OP_CMP[op] % (name , '%s')
            elif op in list(OP_IN.keys()):
                if isinstance(cvalue, str):
                    cvalue = cvalue.split(',')
                elif not isinstance(cvalue, list) and not isinstance(cvalue, tuple):
                    raise SQLError('条件格式错误: %s' % cname)
                else:
                    pass
                # elements of in condition
                nelmts = len(cvalue)
                return OP_IN[op] % (name, ','.join(['%s' for i in range(0, nelmts)]))
            elif op in list(OP_LIKE.keys()):
                return OP_LIKE[op] % (name, '%s')
            elif op in list(OP_NULL.keys()):
                if cvalue not in [True, False]:
                    raise SQLError('条件格式错误: %s' % cname)
                return OP_NULL[cvalue]
            else:
                raise SQLError('条件格式错误：%s' % cname)

        else:
            raise SQLError('条件格式错误：%s' % cname)


Q = _Query


class QuerySet:
    """
        query set
    """
    def __init__(self, db, modelcls, *q, **filters):
        """
            init query object by model class & filters
        :param modelcls:
        :param filters:
        """
        self._db = db
        self._modelcls = modelcls

        self._query = Q(*q, **filters) if len(filters)!=0 or len(q)!=0 else None
        self._groupby = None
        self._orderby = None
        self._limit = None

    def groupby(self, *cols):
        """

        :param cols:
        :return:
        """
        if not set(cols).issubset(self._modelcls.fieldcodes()):
            raise SQLError('group by columns %s not in table fields' % str(*cols))

        if len(cols) != 0:
            self._groupby = ' group by ' + '`' + '`, `'.join(cols) + '`'
        return self

    def orderby(self, *cols):
        """

        :param cols:
        :return:
        """
        if not set(cols).issubset(self._modelcls.fieldcodes()):
            raise SQLError('order by columns %s not in table fields' % str(*cols))

        if len(cols) != 0:
            self._orderby = ' order by ' + '`' + '`, `'.join(cols) + '`'
        return self

    def asc(self):
        """

        :return:
        """
        if self._orderby is not None:
            self._orderby += ' asc'
        return self

    def desc(self):
        """

        :return:
        """
        if self._orderby is not None:
            self._orderby += ' desc'
        return self

    def limit(self, *args):
        """
            get records: limit results start from @pos with @count records
        :param count:
        :param pos:
        :return:
        """
        if not 1<=len(args)<=2:
            raise SQLError('limit grammar %s not support.' % str(*args))

        limits = [str(arg) for arg in args]
        self._limit = ' limit %s' % ','.join(limits)

        return self

    def all(self):
        """
            get records: all
        :return:
        """
        # execute query
        results = self._db.select(self.sqlselect, self.sqlargs)

        # convert to model
        objs = []
        for result in results:
            objs.append(self._modelcls(**result))

        return objs

    def one(self):
        """
            get records: the first record
        :return:
        """
        # execute query
        results = self._db.select(self.sqlselect, self.sqlargs)
        if len(results) > 0:
            return self._modelcls(**results[0])
        return None

    def has(self):
        """
            has records
        :return:
            boolean
        """
        return self.one() is not None

    def update(self, **colvals):
        """
            update records
        :param colvals: dict, column name->value
        :return:
            number of records updated
        """
        if len(colvals)==0 or not set(colvals.keys()).issubset(self._modelcls.fieldcodes()):
            raise SQLError('update columns %s not in table fields' % str(tuple(colvals.keys())))

        # sql string
        sql = ''

        # update clause
        sql += 'update ' + '`' + self._modelcls.tablename() + '`'
        # set clause
        sql += ' set `' + '`=%s, `'.join(colvals.keys()) + '`=%s '
        # where clause
        if self._query is not None:
            sql += ' where ' + self._query.sql()

        # args
        args = list(colvals.values())
        if self._query is not None:
            args.extend(self.sqlargs)

        return self._db.update(sql, args)

    def delete(self):
        """
            delete records
        :return:
            number of records deleted
        """
        # sql string
        sql = ''

        # delete clause
        sql += 'delete from ' + '`' + self._modelcls.tablename() + '`'

        # where clause
        if self._query is not None:
            sql += ' where ' + self._query.sql()

        return self._db.delete(sql, self.sqlargs)

    def insert(self, model):
        """
            insert a object
        :param model:
        :return:
            number of records inserted
        """
        # sql string
        sql = ''

        # table clause #
        sql += 'insert into `' + self._modelcls.tablename() + '`'

        # columns clause #
        columns = self._modelcls.fieldcodes(noauto=True)
        sql += '(' + '`' + '`,`'.join(columns) + '`)'

        # add ? clause
        v = []
        for i in range(len(columns)):
            v.append('%s')
        sql += ' values (' + ','.join(v) + ')'

        affects = self._db.insert(sql, model.values(noauto=True))
        if affects > 0:
            model.setauto(self._db.lastrowid())
        return model

    @property
    def sqlselect(self):
        """
            select sql
        :return:
        """
        # sql string
        sql = ''

        # select clause
        sql += 'select ' + '`' + '`,`'.join(self._modelcls.fieldcodes()) + '`'
        # from clause
        sql += ' from ' + '`' + self._modelcls.tablename() + '`'
        # where clause
        if self._query is not None:
            sql += ' where ' + self._query.sql()
        # group by clause
        sql += self._groupby or ''
        # order by clause
        sql += self._orderby or ''
        # limit clause
        sql += self._limit or ''

        return sql

    @property
    def sqlargs(self):
        """
            sql arguments
        :return:
        """
        return self._query.args() if self._query is not None else None
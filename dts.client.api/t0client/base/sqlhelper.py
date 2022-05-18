"""
    sql generator
"""
import copy


class SQLError(Exception):
    """
        sql helper error
    """
    def __init__(self, msg):
        self._msg = msg

    @property
    def msg(self):
        return self._msg

    def __str__(self):
        return self._msg

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

    def __deepcopy__(self, memodict):
        obj = _Node(connector=self.connector, negated=self.negated)
        obj.__class__ = self.__class__
        obj.children = copy.deepcopy(self.children, memodict)
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
            else:
                raise SQLError('条件格式错误：%s' % cname)

        else:
            raise SQLError('条件格式错误：%s' % cname)

Q = _Query


class _Select:
    """
        select sql
    """
    def __init__(self):
        self._table = None
        self._columns = None
        self._where = None
        self._orderby = None
        self._order = None
        self._groupby = None
        self._limit = None

    def columns(self, *cols):
        """

        :param cols: array|tupple, columns
        :return:
        """
        self._columns = cols
        return self

    def table(self, tbl):
        """

        :param tbls:
        :return:
        """
        self._table = tbl
        return self

    def where(self, *args, **kwargs):
        """

        :param conds:
        :return:
        """
        self._where = Q(*args, **kwargs)
        return self

    def orderby(self, *cols):
        """

        :param cols:
        :return:
        """
        self._orderby = cols
        return self

    def groupby(self, *cols):
        """

        :param cols:
        :return:
        """
        self._groupby = cols
        return self

    def asc(self):
        """

        :return:
        """
        self._order = 'asc'
        return self

    def desc(self):
        """

        :return:
        """
        self._order = 'desc'
        return self

    def limit(self, count, pos=0):
        """
            limit results start from @pos with @count records
        :param count:
        :param pos:
        :return:
        """
        self._limit = '%d,%d' % (pos, count)
        return self

    def sql(self):
        """

        :return:
        """
        # sql string
        s = ''

        # select clause
        if self._columns is None:
            raise SQLError('查询语句没有指定列')
        s = s + 'select ' + '`' + '`,`'.join(self._columns) + '`'

        # from clause
        if self._table is None:
            raise SQLError('查询语句没有指定表')
        s = s + ' from ' + '`' + self._table + '`'

        # where clause
        whereclause = self._where.sql()
        if whereclause:
            s = s + ' where ' + whereclause

        # group by clause
        if self._groupby is not None:
            s = s + ' group by ' + '`' + '`, `'.join(self._groupby) + '` '

        # order by clause
        if self._orderby is not None:
            s = s + ' order by ' +'`' + '`, `'.join(self._orderby) + '` '

        # order clause
        if self._order is not None:
            s = s + self._order

        # limit clause
        if self._limit is not None:
            s = s + ' ' + self._limit

        return s

    def args(self):
        """

        :return:
        """
        return self._where.args()


select = _Select


class _Insert:
    """
        insert sql helper
    """
    def __init__(self):
        self._table = None
        self._columns = None
        self._values = None

    def colvals(self, **cvals):
        """

        :param cvals:
        :return:
        """
        self._columns = list(cvals.keys())
        self._values = list(cvals.values())
        return self

    def columns(self, *cols):
        """

        :param cols: array|tupple, columns
        :return:
        """
        self._columns = cols
        return self

    def table(self, tbl):
        """

        :param tbl:
        :return:
        """
        self._table = tbl
        return self

    def values(self, *vals):
        """

        :param conds:
        :return:
        """
        self._values = vals
        return self

    def sql(self):
        """

        :return:
        """
        # sql string
        s = ''

        # table clause #
        if self._table is None:
            raise SQLError('插入语句没有指定表')
        s = s + 'insert into `' + self._table + '` '

        # columns clause #
        if self._columns is None:
            raise SQLError('插入语句没有指定列')
        s = s + '(' + '`' + '`,`'.join(self._columns) + '`) '

        # values clause #
        if self._values is None:
            raise SQLError('插入语句没有指定值')

        # check items
        if len(self._columns) != len(self._values):
            raise SQLError('插入语句列和值不对应')

        # add ? clause
        v = []
        for i in range(len(self._columns)):
            v.append('%s')
        s = s + 'values (' + ','.join(v) + ')'

        return s

    def args(self):
        """

        :return:
        """
        return self._values


insert = _Insert


class _Update:
    """
        update sql
    """
    def __init__(self):
        self._table = None
        self._cvals = None
        self._where = None

    def set(self, **cvals):
        """

        :param cols: array|tupple, columns
        :return:
        """
        self._cvals = cvals
        return self

    def table(self, tbl):
        """

        :param tbls:
        :return:
        """
        self._table = tbl
        return self

    def where(self, *args, **kwargs):
        """

        :param conds:
        :return:
        """
        self._where = Q(*args, **kwargs)
        return self

    def sql(self):
        """

        :return:
        """
        # sql string
        s = ''

        # update clause
        if self._table is None:
            raise SQLError('更新语句没有指定表')
        s = s + 'update ' + '`' + self._table + '` '

        # set clause
        if self._cvals is None:
            raise SQLError('更新语句没有指定值')
        s = s + 'set `' + '`=%s, `'.join(self._cvals.keys()) + '`=%s '

        # where clause
        whereclause = self._where.sql()
        if whereclause:
            s = s + 'where ' + whereclause

        return s

    def args(self):
        """

        :return:
        """
        vals = []

        # value args
        vals.extend(self._cvals.values())

        # where args
        vals.extend(self._where.args())

        return tuple(vals)


update = _Update


class _Delete:
    """
        delete sql
    """
    def __init__(self):
        self._table = None
        self._where = None

    def table(self, tbl):
        """

        :param tbls:
        :return:
        """
        self._table = tbl
        return self

    def where(self, *args, **kwargs):
        """

        :param conds:
        :return:
        """
        self._where = Q(*args, **kwargs)
        return self

    def sql(self):
        """

        :return:
        """
        # sql string
        s = ''

        # delete clause
        if self._table is None:
            raise SQLError('更新语句没有指定表')
        s = s + 'delete from ' + '`' + self._table + '` '

        # where clause
        whereclause = self._where.sql()
        if whereclause:
            s = s + 'where ' + whereclause

        return s

    def args(self):
        """

        :return:
        """
        return self._where.args()


delete = _Delete


class _Util:
    @staticmethod
    def repeat(s, cnt, sep):
        """
            repeat string by @s for @cnt times with separator @sep
        :param s:
        :param cnt:
        :param sep:
        :return:
        """
        v = []
        for i in range(0, cnt):
            v.append(s)
        return sep.join(v)


util = _Util


if __name__ == '__main__':
    s = select().columns('a', 'b').table('tb1').where(Q(a__lt=1)&(Q(b__ge=2)|Q(b__in=('x','y')))).orderby('a').desc()
    print(s.sql())
    print(s.args())

    s = insert().columns('a', 'b').table('tb1').values(1, 'a')
    print(s.sql())
    print(s.args())

    s = update().table('tb1').set(a=1, b='b').where(c=0)
    print(s.sql())
    print(s.args())

    s = delete().table('tb1').where(a=1, b=2)
    print(s.sql())
    print(s.args())

    print(util.repeat('?', 10, ','))

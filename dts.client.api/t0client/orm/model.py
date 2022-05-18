"""
    pub model base class
"""
from . import field, query


class ModelError(Exception):
    pass


class MetaModel(type):
    def __new__(cls, name, bases, attrs):
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)

        #get declared fields
        fields, autofield = {}, None
        for code, f in attrs.items():
            if issubclass(f.__class__, field.Field):
                if fields.get(code) is not None:
                    raise ModelError('duplicate model field: %s'%str(code))

                f.code = code
                if f.name is None:
                    f.name = code
                fields[code] = f

                if f.__class__ == field.AutoField:
                    if autofield is not None:
                        raise ModelError('duplicate model auto field %s with %s, only one auto field permitted.' % (autofield, str(code)))

                    autofield = code

        # remove declare in attrs
        for k in fields.keys():
            del attrs[k]

        # auto field name
        attrs['__auto__'] = autofield
        # table name
        attrs['__table__'] = attrs.get('__table__', name)
        # model fields
        attrs['__fields__'] = fields

        return type.__new__(cls, name, bases, attrs)


class Model(dict, metaclass=MetaModel):
    def __init__(self, **kwargs):
        if hasattr(self.__class__, '__fields__'):
            super().__init__()
            for code, field in self.fields().items():
                self[code] = field.value(kwargs.get(code, field.default))
        else:
            super().__init__(**kwargs)

    def __getattr__(self, code):
        return self[code]

    def __setattr__(self, code, value):
        self.set(code, value)

    def set(self, code, value):
        """
            set model object code->value
        :param code:
        :param value:
        :return:
        """
        fields = self.fields()
        field = fields.get(code)
        if field is None:
            raise field.ErrorFieldNotExist(code)

        self[code] = field.value(value)

    def values(self, noauto=False):
        """
            object values
        :param noauto: exclude auto field value flag
        :return:
            list
        """
        vals = []
        for code in self.fieldcodes():
            if noauto and self.__auto__ == code:
                continue
            vals.append(self[code])
        return vals

    def fieldvalues(self, noauto=False):
        """
            field->values
        :param noauto:
        :return:
            dict
        """
        fvs = {}
        for k, v in self.items():
            if noauto and k == self.__auto__:
                continue
            fvs[k] = v
        return fvs

    def setauto(self, val):
        """
            set auto field value
        :param val:
        :return:
        """
        if self.__auto__ is not None:
            self[self.__auto__] = val

    @classmethod
    def fields(cls):
        """
            get table fields
        :return:
            dict, name->field
        """
        return cls.__fields__

    @classmethod
    def tablename(cls):
        return cls.__table__

    @classmethod
    def fieldcodes(cls, noauto=False):
        """
            get table fields code
        :param noauto: exclude auto field code flag
        :return:
            list
        """
        codes = []
        for k in cls.__fields__.keys():
            if noauto and cls.__auto__ == k:
                continue
            codes.append(k)
        return codes

    @classmethod
    def fieldnames(cls):
        """
            get table fields name
        :return:
            list
        """
        names = []
        for field in cls.__fields__.values():
            names.append(field.name)
        return names

    @classmethod
    def filter(cls, db, *q, **filters):
        """
            use specified database for query
        :param db: obj, database object
        :param q: obj, query.Q object
        :param filters: dict, filter conditions
        :return:
            query set object
        """
        return query.QuerySet(db, cls, *q, **filters)

    @classmethod
    def all(cls, db):
        """
            get all data
        :param db: obj, database object
        :return:
            list of model object
        """
        return query.QuerySet(db, cls).all()

    def save(self, db):
        """
            save current object to specified db
        :return:
        """
        if self.__auto__ is not None and self[self.__auto__] is not None:
            return query.QuerySet(db, self.__class__, **{self.__auto__:self[self.__auto__]}).update(**self.fieldvalues(True))
        else:
            return query.QuerySet(db, self.__class__).insert(self)

    def update(self, **kvs):
        """
            update model object values
        :param kvs: dict, field->value
        :return:
            self
        """
        for k, v in kvs.items():
            self.set(k, v)
        return self

    def delete(self, db):
        """
            delete model from database
        :return:
        """
        if self.__auto__ is None or self[self.__auto__] is None:
            raise ModelError('model has not an primary key')
        return query.QuerySet(db, self.__class__, **{self.__auto__:self[self.__auto__]}).delete()

    @classmethod
    def select(cls, db, sql, *args):
        """
            select data with raw sql
        :param db: obj, database object
        :param sql: str, sql
        :param args: list/tupple, args for sql
        :return:
            model objects
        """
        objs = []

        results = db.select(sql, *args)
        for result in results:
            objs.append(cls(**result))

        return objs


class RawModel(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __getattr__(self, code):
        return self[code]

    def __setattr__(self, code, value):
        self[code] = value

    @classmethod
    def select(cls, db, sql, *args):
        """
            select data with raw sql
        :param db: obj, database object
        :param sql: str, sql
        :param args: list/tupple, args for sql
        :return:
            model objects
        """
        objs = []

        results = db.select(sql, *args)
        for result in results:
            objs.append(cls(**result))

        return objs

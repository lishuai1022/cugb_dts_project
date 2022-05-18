"""
    pub form base class
"""
from . import field

class MetaForm(type):
    def __new__(cls, name, bases, attrs):
        if name == 'Form':
            return type.__new__(cls, name, bases, attrs)

        #get declared fields
        fields = {}
        for code, f in attrs.items():
            if issubclass(f.__class__, field.Field):
                f.code = code
                if f.name is None:
                    f.name = code
                fields[code] = f

        # remove declare in attrs
        for k in fields.keys():
            del attrs[k]

        # model fields
        attrs['__fields__'] = fields

        return type.__new__(cls, name, bases, attrs)


class Form(dict, metaclass=MetaForm):
    def __init__(self, **kwargs):
        super().__init__()
        for code, field in self.fields().items():
            self[code] = field.value(kwargs.get(code, field.default))

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        field = self.fields().get(name)
        if field is None:
            raise field.ErrorFieldNotExist(name)

        self[name] = field.value(value)

    def values(self):
        """
            object values
        :return:
            list
        """
        vals = []
        for name in self.fieldnames():
            vals.append(self[name])
        return vals

    @classmethod
    def fields(cls):
        """
            get table fields
        :return:
            dict, name->field
        """
        return cls.__fields__

    @classmethod
    def fieldcodes(cls):
        """
            get table fields code
        :return:
            list
        """
        return list(cls.__fields__.keys())

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

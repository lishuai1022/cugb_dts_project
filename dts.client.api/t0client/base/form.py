"""
     base class
"""
from . import field
import decimal

class MetaForm(type):
    def __new__(cls, name, bases, attrs):
        if name == 'Model':
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

        # save fields
        attrs['__fields__'] = fields

        return type.__new__(cls, name, bases, attrs)


class Form(dict, metaclass=MetaForm):
    def __init__(self, **kwargs):
        for code, field in self.__fields__.items():
            self[code] = field.valueof(kwargs.get(code, field.default))

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        field = self.__fields__.get(name)
        if field is None:
            raise field.ErrorFieldNotExist(name)

        self[name] = field.valueof(value)


class TestForm(Form):
    id = field.IntegerField(name='ID', min_value=2)
    name = field.StringField(name='名称', null=True)
    sex = field.EnumField(name='性别', choices=('male', 'female'))
    disable = field.BooleanField(name='禁用')
    money = field.DecimalField(digits=10)


if __name__ == '__main__':
    a = TestForm(id=2, name='abc', sex='male',money=decimal.Decimal('10.222'), disable=True, age=12)
    a.id = 3
    print(a.money)

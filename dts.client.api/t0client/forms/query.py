from .. import base

class Balance(base.form.Form):
    account = base.field.StringField(min_length=1)
    token = base.field.StringField(min_length=32,max_length=32)

class Position(base.form.Form):
    account = base.field.StringField(min_length=1)
    token = base.field.StringField(min_length=32, max_length=32)

    code = base.field.StringField(null=True, default='')

class Order(base.form.Form):
    page = base.field.IntegerField(null=True, default=1)
    pagesize = base.field.IntegerField(null=True, default=20)

class Fill(base.form.Form):
    # order_id = base.field.StringField(null=True,pattern='/{d}*/',default='')
    type = base.field.EnumField(choices=['0','1'])
    page = base.field.IntegerField(null=True,default=1)
    pagesize = base.field.IntegerField(null=True,default=20)
    sdate = base.field.DateField(null=True)
    edate = base.field.DateField(null=True)

class Cancel(base.form.Form):
    page = base.field.IntegerField(null=True, default=1)
    pagesize = base.field.IntegerField(null=True, default=20)

class Money(base.form.Form):
    item = base.field.StringField(default='all')
    page = base.field.IntegerField(null=True, default=1)
    pagesize = base.field.IntegerField(null=True, default=20)
    sdate = base.field.DateField(null=True)
    edate = base.field.DateField(null=True)

class Stockpos(base.form.Form):
    code = base.field.StringField(null=False,min_length=6,max_length=6)

class FillImport(base.form.Form):
    type = base.field.EnumField(choices=['0','1'])
    sdate = base.field.DateField(null=True)
    edate = base.field.DateField(null=True)

class MoneyImport(base.form.Form):
    item = base.field.StringField(default='all')
    sdate = base.field.DateField(null=True)
    edate = base.field.DateField(null=True)


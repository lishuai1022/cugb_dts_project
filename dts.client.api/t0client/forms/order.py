from .. import base

class Place(base.form.Form):
    account = base.field.StringField(min_length=1,max_length=10)
    token = base.field.StringField(min_length=32,max_length=32)

    exchange = base.field.EnumField(choices=('SH','SZ'))
    type = base.field.EnumField(choices=('STK','FUT','OPT'))
    code = base.field.StringField(min_length=6,max_length=6)
    quantity = base.field.IntegerField()
    price = base.field.FloatField(null=True,default=0)
    side = base.field.EnumField(choices=('0','1'))
    ptype = base.field.EnumField(choices=('0','1'))
    currency = base.field.EnumField(choices=('CNY'),default='CNY')

class Cancel(base.form.Form):
    order_id = base.field.StringField()

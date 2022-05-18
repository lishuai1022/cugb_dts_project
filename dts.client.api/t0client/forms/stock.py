from .. import base

class Buy(base.form.Form):
    ccode = base.field.StringField(min_length=6,max_length=6)
    price = base.field.StringField(min_length=1,max_length=6)
    quantity = base.field.StringField(min_length=1)
    tside = base.field.IntegerField(choices=[0,1])
    faccount_id = base.field.IntegerField()


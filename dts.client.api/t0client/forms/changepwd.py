from .. import base

class Changepwd(base.form.Form):
    trader_id = base.field.StringField(min_length=1,max_length=10)
    old_pwd = base.field.StringField(min_length=6,max_length=20)
    new_pwd = base.field.StringField(min_length=6,max_length=20)
from .. import base

class Logout(base.form.Form):
    account = base.field.StringField(min_length=1)
    token = base.field.StringField(min_length=32,max_length=32)
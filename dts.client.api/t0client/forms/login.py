from .. import base

class Login(base.form.Form):
    account = base.field.StringField(min_length=4,max_length=20)
    pwd = base.field.StringField(min_length=6,max_length=20)
    imgcode = base.field.StringField(min_length=4,max_length=4)
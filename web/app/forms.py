from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField, DateField, SelectField
from wtforms.validators import DataRequired


class MyForm(FlaskForm):
    name = TextField('学号', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    date = DateField('开学第一周周一的日期', format='%Y/%m/%d',
                     validators=[DataRequired()])
    reminder = SelectField('提醒时间', choices=[
        ('0', '不提醒'),
        ('1', '课前10分钟提醒'),
        ('2', '课前30分钟提醒'),
        ('3', '课前1小时提醒'),
        ('4', '课前2小时提醒'),
        ('5', '课前1天提醒')
    ], validators=[DataRequired()])

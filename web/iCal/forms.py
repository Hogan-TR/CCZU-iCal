from django import forms
import datetime


class iCalForm(forms.Form):
    username = forms.CharField(
        label='学号', widget=forms.TextInput(), max_length=10)
    password = forms.CharField(label='密码', widget=forms.PasswordInput())
    date = forms.DateField(label='开学第一周周一的日期', initial=datetime.date.today)
    reminder = forms.ChoiceField(label='提醒时间', choices=(
        (0, '不提醒'), (1, '课前10分钟提醒'), (2, '课前30分钟提醒'), (3, '课前1小时提醒'), (4, '课前2小时提醒'), (5, '课前1天提醒')))

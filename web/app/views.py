from app import app
from app.forms import MyForm
from app.funcs import iCalPro, BASE_DIR
from flask import session, request, render_template, redirect, url_for, send_from_directory, flash
import os

import sys
sys.path.append('..')
from config import *


@app.route('/', methods=['GET', 'POST'])
def index():
    form = MyForm()
    if request.method == 'POST':
        if form.validate():
            username = form.data['name']
            password = form.data['password']
            date = form.data['date']
            reminder = form.data['reminder']

            user = iCalPro()
            result = user.iCalPro(username, password, date.strftime(
                '%Y%m%d'), reminder)  # Tuple
            session['res'] = result

            return redirect(url_for('subscribe'))  # 失败处理 flash 消息
        else:
            flash('请检查日期正确性，并以"Year/Month/Day"格式正确填写😬')
    return render_template('index.html', form=form)


@app.route('/subscribe')
def subscribe():
    try:
        res = session['res']
    except:
        return redirect(url_for('index'))

    if res[0]:  # Success
        filename = res[1]
        context = {'link': f"https://{BASE_HOST}" +
                   url_for('download', filename=filename)}
    else:
        error = res[1]
        context = {
            'errortips': error,
            'link_home': url_for('index')
        }
    return render_template('subscribe.html', context=context)


@app.route('/download/<filename>')
def download(filename):
    filepath = os.path.join(BASE_DIR, 'tempfile')
    return send_from_directory(filepath, filename, as_attachment=True, attachment_filename='class_schedule.ics')

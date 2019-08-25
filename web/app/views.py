from app import app
from flask import render_template


@app.route('/',methods=['GET','POST'])
def index():
    return render_template('iCal.html')

from web.settings import BASE_DIR
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from .forms import iCalForm
from .funcs import iCalPro

import sys
import os
import datetime
import time

sys.path.append('../')


def index(request):
    if request.method == 'POST':
        form = iCalForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            date = form.cleaned_data['date']
            reminder = form.cleaned_data['reminder']

            user = iCalPro()
            result = user.iCalPro(username, password,
                                  date.strftime('%Y%m%d'), reminder)

            request.session['res'] = result
            return HttpResponseRedirect(reverse('subscribe'))
    else:
        form = iCalForm()

    return render(request, 'iCal/index.html', {'form': form})


def subscribe(request):
    res = request.session.get('res')
    if res[0]:  # Success
        filename = res[1]
        context = {'link': "http://127.0.0.1:8000" +
                   reverse('download', args=(filename,))}
    else:
        error = res[1]
        context = {'errortips': error}
    return render(request, 'iCal/subscribe.html', context)


def download(request, filename):
    filepath = os.path.join(BASE_DIR, f"tempics/{filename}")
    file = open(filepath, "rb")
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

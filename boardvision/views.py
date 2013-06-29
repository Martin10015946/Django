import os
import json
import datetime
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.http import HttpResponse
from models import BoardHandler, FolderSorter
       
def get_ncfolder_path(shop, week='this_week'):
    path = "//Utl_4/C on Monster" + os.sep + "Today's File"
    if shop == 'garage': path += os.sep + 'Garage'
    if not week == 'this_week': path += os.sep + 'x - Next Week'

    return path

def get_week_nr(folder):
    w = int(datetime.datetime.today().strftime('%W'))
    if folder == 'this_week':
        return w+1
    else:
        return w+2

def get_view_days(path):
    fs = FolderSorter(path)
    days = fs.get_sorted_list()
    view_days = []
    total = 0
    total_ready = 0
    for day in days:
        view_day = {'total':0}
        view_day['total_ready'] = 0
        view_day['boards'] = []
        for board in day:
            bh = BoardHandler(path + os.sep + board)
            b = {}
            b['image'] = bh.get_preview()
            b['path'] = path + os.sep + board
            view_day['boards'].append(b)
            dur =  bh.get_duration()
            view_day['total'] += dur
            total += dur
            if bh.is_ready(): 
                view_day['total_ready'] += dur
                total_ready += dur
        view_days.append(view_day)

    return view_days, total, total_ready

def index(request, shop, folder='this_week'):
    path = get_ncfolder_path(shop, folder)
    data = {}
    data['days'], data['total'], data['total_ready'] = get_view_days(path)
    data['folder'] = folder
    data['shop'] = shop
    data['home_on_server'] = settings.HOME_ON_SERVER 
    data['week_nr'] = get_week_nr(folder)

    return render_to_response('board_vision.html', data, context_instance=RequestContext(request))

def set_status(request):
    if request.POST:
        path = get_ncfolder_path(request.POST['shop'],request.POST['folder'])
        path += os.sep + request.POST['NCName']
        bh = BoardHandler(path)
        if request.POST['NCStatus'] == 'ready':
            bh.set_ready()
        else:
            bh.get_preview(force=True)

    return HttpResponse(json.dumps([]), mimetype='application/json') 
    


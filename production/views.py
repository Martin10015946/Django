import datetime
import json
import urllib2
from math import ceil
from collections import OrderedDict
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings

from production.models import OrderDetail, record_status, Preparation
from progress_report.models import get_rollovers_total


def get_display_hours(minutes):
    if minutes > 0:
        minutes = int(minutes) 
        sign = 1
    else:
        minutes = int(minutes) * -1
        sign = -1

    hours, minutes = divmod(minutes, 60)
    
    if hours <= 9: h='0%s'
    else: h='%s'
    if minutes <= 9: m='0%s'
    else: m='%s'
    
    if sign == 1:
        return (h+':'+m)%(hours, minutes)
    else:
        return ('-'+h+':'+m)%(hours, minutes)

def get_navigation_url(dict):
        
    url_template = dict['url_template']#'/progress_report/%s/%s/%s/'
    week_nr = dict['week_nr']
    year = dict['year']
    shop = dict['shop']
    
    if week_nr == 1:
        next = [int(year), 2]
        previous = [int(year) - 1, 53]
    elif week_nr == 53:
        next = [int(year) + 1, 1]
        previous = [int(year), 52]
    else: 
        next = [year, int(week_nr) + 1]
        previous = [year, int(week_nr) - 1]
    
    previous = url_template%(previous[0],previous[1],shop)
    next = url_template%(next[0],next[1],shop)
    
    today = datetime.datetime.now()
    this_week = str(int(today.strftime('%W'))+1)
    this_year = today.strftime('%Y')
    
    this = url_template%(this_year,this_week,shop)

    return {'next': next, 'previous': previous, 'this': this}

def dashboard(request):
    # I get the number of the week and the year of now to pass to the view    
    today = datetime.datetime.now()
    week = str(int(today.strftime('%W'))+1)
    year = today.strftime('%Y')
    month = today.strftime('%m')

    rollovers = {'bricklane': get_display_hours(get_rollovers_total('bricklane')),
                 'garage': get_display_hours(get_rollovers_total('garage'))}

    preparations = Preparation.objects.all()

    # build a list for the template
    boxes = {}
    for preparation in preparations:
        boxes[preparation.name] = preparation.checked

    data = {'week': week}
    data['year'] = year
    data['month'] = month
    data['rollovers']= rollovers
    data['preparations'] = boxes
    data['home_on_server'] = settings.HOME_ON_SERVER
    data['clear_cache'] = settings.ACCESS_API_URL + 'clear_cache/'

    return render_to_response('landing.html', data,
                               context_instance=RequestContext(request))

def record_preparation(request):
    # function called by javascript/Ajax when the user click the checkbox
    if request.method == 'POST':
        json_value = request.POST.keys()[0] # first occurence because the post pass a string and not an array
        data = json.loads(json_value)

        p = record_status(data)
        return HttpResponse(json.dumps([p]), mimetype='application/json')

def update_fileprep(request):
    if request.method == 'POST':
        od = OrderDetail.objects.get(ac_od_id=request.POST['ac_od_id'])
        od.fileprep = request.POST['fileprep'] # 0 or 1 
        od.save()

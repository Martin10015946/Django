import urllib2
import json
import datetime
import sys
import pprint
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from production.models import OrderDetail, set_day_ETA, week_range
from production.views import get_navigation_url
from utl_timer.models import get_view_day, update_play, update_record, get_timed_product, get_access_order




def day(request, year, month, day, shop):
    """
    Show the timeline and the schedule of the order datails of the selected day year/month/day
    """
    json_url = '%sassembly_list/day/'%(settings.ACCESS_API_URL)
    json_url = json_url + '%s/%s/%s/%s'%(year, month, day, shop)
    j, assy_date = _get_assy_from_json(json_url)
    assy_list = get_view_day(j)
    return render_to_response('utl_timer.html', 
                            {'date': assy_date,
                            'products': assy_list,
                            'home_on_server': settings.HOME_ON_SERVER,
                            'shop': shop}, context_instance=RequestContext(request))

def today(request, shop):
    """
    Show the timeline and the schedule of the order datails
    """
    json_url = '%sassembly_list/%s'%(settings.ACCESS_API_URL,shop)
    j, assy_date = _get_assy_from_json(json_url)
    assy_list = get_view_day(j)
    return render_to_response('utl_timer.html', 
                            {'date': assy_date,
                            'products': assy_list,
                            'home_on_server': settings.HOME_ON_SERVER,
                            'shop': shop}, context_instance=RequestContext(request))

def product(request, year,  week, shop, ac_od_id):
    """
    This functions is called from the progress report. Open the the timing dialog windows directly, skeeping 
    the first windows with the timeline. At the and of the process, the process will go back to the progress report 
    """
    
    json_url = '%sorder_detail/%s'%(settings.ACCESS_API_URL,ac_od_id)

    f = urllib2.urlopen(json_url)
    j = f.read()
    f.close()
    product = json.loads(j)

    return render_to_response('product_utl_timer.html', 
                                {
                                'product': product,
                                'home_on_server': settings.HOME_ON_SERVER,
                                'week': week,
                                'year': year,
                                'shop': shop}, context_instance=RequestContext(request))

def week(request, year, week, shop):
    """
    Week Timer Report
    """

    # get the orders from local table
    wlist = week_range(int(year),int(week))
    monday = wlist[0]
    sunday = wlist[6]
    local_ods = get_timed_product(monday, sunday, shop)
    local_ods = local_ods.order_by('start_time')

    # get the order detail from access db with the id of the local timed order detail
    access_orders = get_access_order(local_ods)

    # definition of the variables for the merging
    date_format = '%A %d %B'
    # the current date has to be iniatialize out of loop with the date of the first order
    current_day = local_ods[0].start_time.strftime(date_format)
    current_day_list = []
    days = {}
    template_data = []

    # merging the two result set
    for od in local_ods:
        ac_order = {}
        for el in access_orders:
            if el['ac_od_id'] == od.ac_od_id:
                ac_order = el
                ac_order['actual'] = od.actual
                ac_order['pause'] = od.pause
                ac_order['total'] = od.pause + od.actual
                ac_order['status'] = od.status
                ac_order['start_time'] = od.start_time.strftime('%Y/%m/%d %H:%M:%S')
                ac_order['class'] = 'product timed'

        if od.start_time.strftime(date_format) == current_day:
            # append the order in the list
            current_day_list.append(ac_order)
        else:
            # append the order in the list, create a new assemble day in the dictionary, clean the temporary variables
            days[current_day] = current_day_list
            template_data.append(days)
            days = {}
            current_day = od.start_time.strftime(date_format)
            current_day_list = [] # empty the current day list
            current_day_list.append(ac_order)

    # last time out the loop
    days[current_day] = current_day_list
    template_data.append(days)
    days = {}

    # navigation url
    nav_dict = {}
    nav_dict['url_template'] = '/records/week/%s/%s/%s/'    
    nav_dict['week_nr'] = week    
    nav_dict['year'] = year    
    nav_dict['shop'] = shop    

    return render_to_response('week_utl_timer.html', 
                                {'week_nr': week,
                                 'week': template_data,
                                 'home_on_server': settings.HOME_ON_SERVER,
                                 'navigation': get_navigation_url(nav_dict),
                                 'shop': shop}, context_instance=RequestContext(request))

def _get_assy_from_json(url):
    f = urllib2.urlopen(url)
    j = f.read()
    f.close()
    assy_list = json.loads(j)
    assy_list = assy_list[0]
    assy_date = assy_list.keys()[0]
    assy_list = assy_list[assy_date]
    return assy_list, assy_date
    
def play(request):
    if request.method == 'POST':
        json_value = request.POST.keys()[0] # first occurence because the post pass a string and not an array 
        data = json.loads(json_value) 
        p = update_play(data)
        return HttpResponse(json.dumps(p.id), mimetype='application/json') 
    else: 
        return HttpResponse(json.dumps(['ko']), mimetype='application/json')     

def record(request):
    # called when the assembly person confirms after having pressed record
    if request.method == 'POST':
        json_value = request.POST.keys()[0]
        data = json.loads(json_value)
        p = update_record(data)
        return HttpResponse(json.dumps(p.id), mimetype='application/json') 
    else: 
        return HttpResponse(json.dumps(['ko']), mimetype='application/json')         

def test(request):
    shop = 'garage'
    json_url = '%sassembly_list/%s'%(settings.ACCESS_API_URL,shop)
    assy_list, assy_date = _get_assy_from_json(json_url)
    l = set_day_ETA(assy_list)
    return HttpResponse(json.dumps(l), mimetype='application/json')

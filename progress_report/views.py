import urllib2
import urllib
import json
import datetime
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.contrib.sites.models import Site
from production.views import get_navigation_url, get_display_hours
from utl_timer.models import get_access_order
import production
from boardvision.views import get_ncfolder_path, get_view_days
import progress_report as pr
import manual

def _get_day_link(date_str):
    """
    Function for the links in the progress report to records/day/....
    """
    pass

def _get_rollovers_string(shop):
    rollover = pr.models.get_rollovers_total(shop)
    return get_display_hours(rollover)

def rollovers(request, shop):
    s = _get_rollovers_string(shop)
    return HttpResponse(json.dumps([s]), mimetype='application/json')

def index(request, year, week_nr, shop):
    """
    Progress report - Display one week order details grouped by day.
    Access DB has the order details that we are making.
    Local DB records production events (lamination, machining, assembly and rats).
    Rollovers (OD not ready from past weeks) are displayed on top.
    This view calculates that ETA of the order details planned today.
    This updates the calculation of "rollovers".
    """

    data = {'year': year, 'week_nr': week_nr, 'shop': shop}

    nav_dict = {}
    nav_dict['url_template'] = '/progress_report/%s/%s/%s/'    
    nav_dict['week_nr'] = week_nr    
    nav_dict['year'] = year
    nav_dict['shop'] = shop
    data['navigation'] = get_navigation_url(nav_dict)

    data['tooltips'] = manual.models.get_pr_tooltips()


    rollovers = pr.models.get_rollovers_list(shop)

    #rollovers = list(rollovers)
    # adding orders assembled, planned in the previous weeks, with rat in the current week
    rats = pr.models.get_rollover_rats(shop, 1)


    week = [{'Rollovers': rollovers}]
    
    # Get the week assembly list from Access DB
    url = '%sprogress_report/%s/%s/%s'%(settings.ACCESS_API_URL,year,week_nr,shop)
    f = urllib2.urlopen(url)
    j = f.read()
    f.close()
    week += json.loads(j)

    data['week'] = [] 
    data['total_plan_week'] = 0
    for day in week: 

        if day.keys()[0] is 'Rollovers':
            ods = day['Rollovers']
            date = 'Rollovers'
        else:
            date = day.keys()[0]
            today = datetime.datetime.today().strftime('%A %d %B') 
            if date == today: # calculate the ETA
                ods = production.models.set_day_ETA(day[date])
            else: # set at generic ETA on the morning of the planned date
                date_obj = datetime.datetime.strptime(year + ' ' + date, '%Y %A %d %B')
                ods = []
                for od in day[date]:
                    od['ETA'] = date_obj.strftime('%Y/%m/%d %H:%M:%S')
                    ods.append(od)

        total_plan_day = 0 
        for od in ods:
            # update totals
            total_plan_day += int(od['plan']) 
            # get local info
            od = pr.models.get_pr_od(od, shop)

        data['total_plan_week'] += total_plan_day
        data['week'].append([date, ods, total_plan_day])
    
    data['rollover'] = pr.models.get_rollovers_total(shop)
    data['assembly_buffer'] = pr.models.get_assembly_buffer(shop)
    try:
        path = get_ncfolder_path(shop, 'this_week')
        x, y, data['machining_buffer'] = get_view_days(path)
    except:
        data['machining_buffer'] = 0

    data['home_on_server'] = settings.HOME_ON_SERVER
    data['domain'] = Site.objects.get_current().domain
    data['access_api_url'] = settings.ACCESS_API_URL

    data['rat_reasons'] = pr.models.get_rat_reasons()

    return render_to_response('progress_report.html', data, 
            context_instance=RequestContext(request))

def record(request):
    '''
    Record the Laminated/Machine/Assembled
    status of an order detail.
    '''
    if request.method == 'POST':
        json_value = request.POST.keys()[0] # first occurence because the post pass a string and not an array 
        data = json.loads(json_value)
        p = pr.models.record_status(data)

        # this is to update the Access Db
        if data['name'] == 'assembled':
            if data['record'] == 1:
                access_post_data = [('id', data['ac_od_id']),('status','Ready')]
            elif data['record'] == 0:
                access_post_data = [('id', data['ac_od_id']),('status','To make')]
    
            result = urllib2.urlopen(
                    settings.ACCESS_API_URL+'order_detail/update_status/',
                    urllib.urlencode(access_post_data))

            r = result.read()
        else:
            r = None

        return HttpResponse(json.dumps([p]), mimetype='application/json')

def noise(request):
    """
    All the order details not ready in the past
    with no required date or a required in the past (not this week)
    """
    url = settings.ACCESS_API_URL + 'noise'
    f = urllib2.urlopen(url)
    j = f.read()
    f.close()
    noise = json.loads(j)
    total = get_display_hours(noise[0])  
    
    return render_to_response(
                'noise.html'
                ,{'noise' : noise, 'total': total, 'home_on_server' : settings.HOME_ON_SERVER}
                , context_instance=RequestContext(request)
                )

def line_ups(request):
    '''
    List the order details according to their delivery date
    and the type of delivery / pick up.
    '''
    #1. get the  list
    url = '%sline_ups/'%(settings.ACCESS_API_URL)
    f = urllib2.urlopen(url)
    j = f.read()
    f.close()
    data = json.loads(j)
    week = data['week']
    days = [] # list that will be passed to the template
    total_plan_week = 0

    for day in week:

        total_plan_day = 0
        date = day.keys()[0]

        # dictionary will contain the orders splitted by package type
        od_by_package = {}

        for od in day[date]:
            od = pr.models.get_line_ups_od(od)

            if od['assembled'] == 0:
                od['plan'] = int(od['plan'])
                total_plan_day += od['plan']

            if od['note'] == None:
                od['note'] = ""

            # add to every order the package information
            if od_by_package.has_key(od['package_type']):
                od_by_package[od['package_type']].append(od)
            else:
                od_by_package[od['package_type']] = []
                od_by_package[od['package_type']].append(od)

        total_plan_week += total_plan_day
        total_plan_day = str(datetime.timedelta(minutes=total_plan_day))[0:4]
        days.append([date, od_by_package, total_plan_day])


    sum = 0
    for od in data['past']:
        sum = sum + od['plan']
        if od['shop'] == 'Bricklane':
            od['shop'] = 'BR'
        else:
            od['shop'] = 'GR'

    # formatting rollover's total plan
    rollover_plan_total = datetime.timedelta(minutes=sum)
    rollover_plan_total = str(rollover_plan_total)
    rollover_plan_total = rollover_plan_total[0:4]

    tooltips = manual.models.get_lu_tooltips()

    return render_to_response('line_ups.html',
                {'week': days,
                 'past': data['past'],
                 'total_plan_week': get_display_hours(minutes=total_plan_week),
                 'rollover_plan_total': rollover_plan_total,
                 'tooltips': tooltips,
                 'home_on_server' : settings.HOME_ON_SERVER},
            context_instance=RequestContext(request))

def landpage_line_ups(request):
    '''
    List the order details according to their delivery date
    and the type of delivery / pick up.
    '''

    url = '%sline_ups/'%(settings.ACCESS_API_URL)
    f = urllib2.urlopen(url)
    j = f.read()
    f.close()
    data = json.loads(j)
    week = data['week']

    days = [] # list that will be passed to the template
    total_plan_week = 0

    time_today = ""
    time_tomorrow = ""
    time_day_after = ""

    D = datetime.datetime.today()
    T = D + datetime.timedelta(days=1)
    T2 = T + datetime.timedelta(days=1)

    today = datetime.datetime.strftime(D,'%A %d %B')
    tomorrow = datetime.datetime.strftime(T,'%A %d %B')
    day_after = datetime.datetime.strftime(T2,'%A %d %B')

    for day in week:

        total_plan_day = 0
        date = day.keys()[0]

        # dictionary will contain the orders splitted by package type
        od_by_package = {}

        for od in day[date]:
            od = pr.models.get_line_ups_od(od)

            if od['assembled'] == 0:
                od['plan'] = int(od['plan'])
                total_plan_day += od['plan']

            # add to every order the package information
            if od_by_package.has_key(od['package_type']):
                od_by_package[od['package_type']].append(od)
            else:
                od_by_package[od['package_type']] = []
                od_by_package[od['package_type']].append(od)

        total_plan_week += total_plan_day
        total_plan_day = str(datetime.timedelta(minutes=total_plan_day))[0:4]
        days.append([date, od_by_package, total_plan_day])

        if date == today:
            time_today = total_plan_day
        elif date == tomorrow:
            time_tomorrow = total_plan_day
        elif date == day_after:
            time_day_after = total_plan_day

    sum = 0
    for od in data['past']:
        sum = sum + od['plan']
        if od['shop'] == 'Bricklane':
            od['shop'] = 'BR'
        else:
            od['shop'] = 'GR'

    # formatting rollover's total plan
    rollover_plan_total = datetime.timedelta(minutes=sum)
    rollover_plan_total = str(rollover_plan_total)
    rollover_plan_total = rollover_plan_total[0:4]

    response = {
         'rollover_plan_total' : rollover_plan_total
        ,'time_today' : time_today
        ,'time_tomorrow' : time_tomorrow
        ,'time_day_after': time_day_after
    }

    return HttpResponse(json.dumps(response), mimetype='application/json')

def record_location(request):
    """
    Record the location of an order detail 
    from the line ups form.
    """
    data = {}
    if request.method == 'POST':
        data['ac_od_id'] = request.POST['ac_od_id']
        data['location'] = request.POST['location']
        pr.models.record_location(data)
        return HttpResponse('ok', mimetype='text/plain')
    else:
        return HttpResponse('ko', mimetype='text/plain')

def order(request, order):
    """
    The order form view. 
    """
    # take the json from access_api
    url = '%sorder/%s'%(settings.ACCESS_API_URL,str(order)) 
    f = urllib2.urlopen(url)
    j = f.read()
    f.close()
    json_order = json.loads(j)
    
    # compute the sum of all the assambly time
    assembly = 0
    # compute the sum of all the unit prices    
    total_pounds = 0
    
    for element in json_order['order_details']:
        assembly = assembly + element['plan']
        total_pounds = total_pounds + element['line_total']
    assembly = get_display_hours(assembly)
    
    return render_to_response(
            'order.html',{
                'order' : json_order,
                'assembly' : assembly, 
                'access_api_url' : settings.ACCESS_API_URL,
                'total_pounds' : total_pounds},
            context_instance=RequestContext(request))        

def record_rat(request):
    """
    Record the rat from the Progress Report 
    """

    data = {}
    if request.method == 'POST':

        data['ac_od_id'] = request.POST['ac_od_id']
        data['source'] = request.POST['source']
        data['reasons'] = request.POST['reasons']
        data['date'] = datetime.datetime.today()

        pr.models.record_rats(data)

        # Update Local table production_orderdetail
        if data['source'] == 'machining':
            name = 'machined'
        elif data['source'] == 'lamination':
            name = 'laminated'
        elif data['source'] == 'assembly':
            name = 'assembled'

        order_data = {'record': 0, 'ac_od_id': data['ac_od_id'], 'name': name}
        pr.models.record_status(order_data)

        # this is to update the Access Db
        if name == 'assembled':
            access_post_data = [('id', data['ac_od_id']),('status','To make')]

            result = urllib2.urlopen(
                settings.ACCESS_API_URL+'order_detail/update_status/',
                urllib.urlencode(access_post_data))
            r = result.read()

        # retrieve the assembly time
        par = {'record': 0, 'ac_od_id': data['ac_od_id'], 'name': name}
        p = pr.models.record_status(par)

        return HttpResponse(p, mimetype='text/plain')
    else:
        return HttpResponse('ko', mimetype='text/plain')
    
def inactive_orders(request):
    """
    Display all records that are:
        1. deleted in access server but still remain in local db
        2.with the planned date = Null
    """
    local_od_not_assembled = pr.models.inactive_orders()
    local_od_not_assembled = local_od_not_assembled.order_by('shop')

    # get the order detail from access db with the id of the local not timed order detail
    access_orders = get_access_order(local_od_not_assembled)

    # list of the possible inactive orders
    od_not_in_access = []
    od_not_planned = []
    # finding all records that dont exist in access
    for od in local_od_not_assembled:

        found = False
        for el in access_orders:
            if el['ac_od_id'] == od.ac_od_id:
                found = True

        if found == False:
            drop = {}
            drop['ac_od_id'] = od.ac_od_id
            drop['assembled'] = od.laminated
            drop['shop'] = od.shop
            drop['location'] = od.location

            od_not_in_access.append(drop)

    # finding all records without planned date
    for el in access_orders:
        if el['planned_date'] == "":
            od_not_planned.append(el)
        if el['planned_date'] == None:
            od_not_planned.append(el)

    if len(od_not_planned) == 0:
        print 'I haven\'t found inactive orders'
        #build a fake damn freaky example

    return render_to_response(
        'inactive_orders.html',{
            'not_in_access':od_not_in_access
            ,'no_planned':od_not_planned
            ,'home_on_server' : settings.HOME_ON_SERVER},
        context_instance=RequestContext(request))

def record_thickness(request):
    """
    Record the thickness from the Progress Report
    """
    if request.method == 'POST':
        json_value = request.POST.keys()[0] # first occurence because the post pass a string and not an array
        data = json.loads(json_value)
        result = pr.models.record_thickness(data)
        return HttpResponse(result, mimetype='text/plain')
    else:
        return HttpResponse('ko', mimetype='text/plain')

def record_fileprep(request):
    """
    Record the thickness from the Progress Report
    """
    if request.method == 'POST':
        data = {'ac_od_id': request.POST['ac_od_id'], 'fileprep': int(request.POST['fileprep']) }
        result = pr.models.record_fileprep(data)
        return HttpResponse(result, mimetype='text/plain')
    else:
        return HttpResponse('ko', mimetype='text/plain')

def test(request):


    someData = 'Hi I am the Server'
    return render_to_response(
                              'test.html',
                               context_instance=RequestContext(request))

def pdf(request):
    """
    This is an example of generating pdf
    """
    import cStringIO as StringIO
    from xhtml2pdf import pisa

    result = StringIO.StringIO()

    html = render_to_response(
        'pdf.html',{
            'ruskin':'John Ruskin' # it is possible to pass variables
        }, context_instance=RequestContext(request))

    pdf = pisa.CreatePDF(html.content, result)
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    return response

def same_material(request, ac_od_id):
    url = '%ssame_material/%s/'%(settings.ACCESS_API_URL,ac_od_id)
    f = urllib2.urlopen(url)
    j = f.read()
    f.close()
    ods = json.loads(j)
    
    for od in ods:
        od = pr.models.get_pr_od(od, '')
        if od['note'] == None: od['note'] = ""

    data = {}
    data['material'] = ods[0]['material']['board'] 
    data['ods'] = ods
    data['domain'] = Site.objects.get_current().domain 
    data['home_on_server'] = settings.HOME_ON_SERVER

    return render_to_response(
                              'same_material.html', 
                               data, 
                               context_instance=RequestContext(request))

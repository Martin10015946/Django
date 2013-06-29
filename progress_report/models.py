import datetime
import urllib2
import urllib
import json
from collections import OrderedDict
from django.conf import settings
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from production.models import OrderDetail, Rat, RatReason

def _get_display_hours(minutes):
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

def get_line_ups_od(json_od):

    db_od = OrderDetail.objects.filter(ac_od_id=json_od['ac_od_id'])

    if json_od['shop'] == 'Battersea':
        json_od['shop'] = 'GR'
    else: 
        json_od['shop'] = 'BL'

    if db_od:
        db_od = db_od[0]
        json_od['laminated'] = db_od.laminated
        json_od['machined'] = db_od.machined
        json_od['assembled'] = db_od.assembled
        json_od['local_status'] = db_od.status

        json_od['location'] = db_od.location
    
        json_od['Lrat'] = get_rat(db_od.ac_od_id, 'L')
        json_od['Mrat'] = get_rat(db_od.ac_od_id, 'M')
        json_od['Arat'] = get_rat(db_od.ac_od_id, 'A')

        # calculate if the order detail is rollover or not and record the information to the rollover
        eta_db = db_od.get_object_view()
        if 'eta' in eta_db:
            eta = datetime.datetime.strptime(eta_db['eta'],'%Y/%m/%d %H:%M:%S')
            now = datetime.datetime.today()
            if eta < now and db_od.assembled == 0:
                json_od['rollover'] = True
            else:
                json_od['rollover'] = False
        else:
            json_od['rollover'] = False
    else: # if we are here then this order detail was never planned
        if json_od['status'] == 'Ready':
            json_od['laminated'] = 1
            json_od['machined'] = 1
            json_od['assembled'] = 1 
            json_od['local_status'] = 'Ready'
        else:
            json_od['laminated'] = 0
            json_od['machined'] = 0
            json_od['assembled'] = 0 
            json_od['local_status'] = 'To Make'

    return json_od

def get_pr_od(json_od, shop):
    """
    Get (or create) OrderDetail to display in Progress Report 
    """
    
    db_od, created = OrderDetail.objects.get_or_create(ac_od_id= json_od['ac_od_id'])

    if 'ETA' in json_od:
        date = datetime.datetime.strptime(json_od['ETA'],'%Y/%m/%d %H:%M:%S')
        db_od.eta = date

    db_od.shop = shop

    db_od.plan = json_od['plan']
    
    db_od.save()

    if db_od.fileprep == None:
        json_od['fileprep'] = 0 
    else:
        json_od['fileprep'] = db_od.fileprep

    json_od['laminated'] = db_od.laminated
    json_od['machined'] = db_od.machined
    json_od['assembled'] = db_od.assembled
    json_od['local_status'] = db_od.status
    json_od['production_note'] = db_od.production_note
    if db_od.thickness != None:
        json_od['thickness'] = db_od.thickness
    else:
        json_od['thickness'] = " "

    json_od['Lrat'] = get_rat(db_od.ac_od_id, 'lamination')
    json_od['Mrat'] = get_rat(db_od.ac_od_id, 'machining')
    json_od['Arat'] = get_rat(db_od.ac_od_id, 'assembly')

    b = settings.NC_FILES_FOLDER 
    l = json_od['link']
    json_od['link'] = 'file://///%s\%s\%s\%s'%(b,l[0],l[1],l[2])
    
    if json_od['note'] == None: json_od['note'] = ""
    
    return json_od 

def get_rollover_rats(shop, assembled):
    """
    get all the orders planned in the previous weeks but with a rat declared this week
    """
    current_week = int(datetime.datetime.today().strftime('%U'))+1
    order_rats = []

    rats = Rat.objects.all()
    for rat in rats:
        # if rat date is not null
        if rat.date:
            rat_week = int(rat.date.strftime('%U')) + 1
            # if the rat belongs to the current week
            if rat_week == current_week:
                try:
                    order = OrderDetail.objects.get(ac_od_id=rat.ac_od_id, assembled=assembled, shop=shop)
                    order_week = int(order.eta.strftime('%U')) + 1
                    # if the order was scheduled in the past weeks
                    if order_week < current_week:
                        order_rats.append(order)
                except:
                    pass

    return order_rats

def get_rollovers(shop):
    """
    Sum of the assembly time of all the order details 
    not ready and with an ETA in the past
    """
    ods = OrderDetail.objects.filter(assembled=0)
    ods = ods.filter(shop=shop)
    ods = ods.filter(eta__lt=datetime.datetime.now())
    ods = ods.order_by('eta')

    rollovers = 0
    for od in ods:
        rollovers += od.plan

    return ods, rollovers

def get_pulled(shop):
    """
    Sum of the assembly time of all the order details
    ready (assembled) and with an ETA in the future
    """
    ods = OrderDetail.objects.filter(assembled=1)
    ods = ods.filter(shop=shop)
    ods = ods.filter(eta__gt=datetime.datetime.now())
    pulled = 0
    for od in ods: pulled += od.plan

    return ods, pulled

def get_rollovers_total(shop):
    ods, r = get_rollovers(shop)
    ods, p = get_pulled(shop)
    return r - p

def get_order_detail(ac_od_id):
    """
    get the single order detail by ac_od_id
    """
    od = OrderDetail.objects.get(ac_od_id=ac_od_id)
    return od

def record_status(data):
    p = OrderDetail.objects.get(ac_od_id=data['ac_od_id'])
    if data['name'] == 'laminated':
        p.laminated = data['record']
        # if laminated is unticked, set to 0 OrderDetail.thickness
        if data['record'] == 0:
            p.thickness = None
    elif data['name'] == 'machined':
        p.machined = data['record']
    elif data['name'] == 'assembled':
        p.assembled = data['record']
        if data['record'] == 1:
            p.assembled_time = datetime.datetime.now()
        elif data['record'] == 0:
            p.assembled_time = None

    p.save()
    s = get_assembly_buffer(p.shop)
    return _get_display_hours(s)

def get_assembly_buffer(shop):
    """
    The sum of all products ready to be assembled: 
    laminated=1, machined=1, assembled=0
    """
    q = OrderDetail.objects.filter(assembled=0, machined=1, shop=shop)
    s = 0
    for od in q:
        s += od.plan
    return s
    
def get_rollover_weeks(shop):
    """
    Calculate the sum of eollover splitted by week and
    return in a list of tuples 
    """
    d = {}
    ods, r = get_rollovers(shop)

    for od in ods:
        week = int(od.eta.strftime('%W'))+1
        if d.has_key(week):
            d[week] += int(od.plan)
        else:
            d[week] = int(od.plan)

    # remove the pulled from this week
    this_week = int(datetime.datetime.today().strftime('%W'))+1 
    if d.has_key(this_week):
        d[this_week] = d[this_week] - get_pulled(shop)[1]  

    # build the return list of (week, '00:00') tuples
    l = []
    d = sorted(d.items()) # sort dictionary by week
    for key, minutes in d:
        formatted_time = _get_display_hours(minutes)
        l.append((key,formatted_time))

    return l 

def record_rats(data):

    rat = Rat.objects.create(
             ac_od_id=data['ac_od_id']
            ,source=data['source']
            ,reason=data['reasons']
            ,date=data['date'])
    rat.save()

def record_location(data):
    """
    record the location on the local table ordetail
    """
    product = OrderDetail.objects.get(ac_od_id=data['ac_od_id'])
    product.location = data['location']
    return product.save()

def record_thickness(data):
    """
    record the thickness on the local table order detail
    """
    product = OrderDetail.objects.get(ac_od_id=data['ac_od_id'])
    product.thickness = data['thickness']
    return product.save()

def record_fileprep(data):
    """
    record the status of file preparation
    """
    order_detail = OrderDetail.objects.get(ac_od_id=data['ac_od_id'])
    order_detail.fileprep = data['fileprep']
    return order_detail.save()

def get_rat(id, src):
    rat = Rat.objects.filter(ac_od_id=id, source=src)

    if len(rat)>=1:
        rat = rat[0]
    else: 
        rat = None
    return rat

def get_rat_reasons():
    sources = ['lamination','machining','assembly']
    rat_reasons = {}
    for source in sources:
        rat_reasons[source] = RatReason.objects.filter(source=source).order_by('reason')
    return rat_reasons

def get_rollovers_list(shop):
    # get rollovers from local db
    t = datetime.datetime.today()
    t = t.replace(hour=0,minute=0,second=0,microsecond=0)
    m = t - datetime.timedelta(days=t.weekday())
    l, total = get_rollovers(shop)
    l = l.filter(eta__lt=m)
    l = l.order_by('ac_od_id')

    # add to the rollover list the orders ready, planned in the previous weeks, with rats of the current
    roll_rat = get_rollover_rats(shop,1)
    l = list(l) # casting of queryset into list in order to add roll_rat
    l = l + roll_rat

    # POST ids to the access_api
    ids = [od.ac_od_id for od in l]

    url = settings.ACCESS_API_URL + 'order_details/'
    param = urllib.urlencode({'ids':json.dumps(ids)})
    f = urllib2.urlopen(url,param)
    j = f.read()
    f.close()
    jrl = json.loads(j)

    # Group rollovers order details by orders
    # Cant't do this with our local data (no order id there)
    orders = OrderedDict()
    for od in jrl:
        for local_order in l:
            if od['ac_od_id'] == local_order.ac_od_id:
                if orders.has_key(od['ac_o_id']):
                    orders[od['ac_o_id']].append(od)
                else:
                    orders[od['ac_o_id']] = [od]
    rl = []
    for key,val in orders.items():
        for od in val:
            rl.append(od)

    return rl

def inactive_orders():
    """
    inactive orders report
    """
    q = OrderDetail.objects.filter(assembled=0)
    return q

def delete_orders_by_id(request):
    """
    Delete OrderDetail records by ac_od_id
    """
    json_value = request.POST.keys()[0] # first occurence because the post pass a string and not an array
    data = json.loads(json_value)

    # deleting local OrderDetail record
    for order_detail in data:
        record = OrderDetail.objects.get(ac_od_id=int(order_detail))
        record.delete()

    return HttpResponse(json.dumps('ok'), mimetype='application/json')

def blank_future_eta(request):
    """
    set eta field to all records with Eta > today
    """
    today = datetime.datetime.today()
    today = today.date()

    orders = OrderDetail.objects.filter(eta__gt=today)
    for order in orders:
        order.eta = None
        order.save()

    return HttpResponse('ok', mimetype='text/plain')

def record_plan(request):
    """
    record plan by ac_od_id
    """
    ac_od_id =  request.POST['ac_od_id']
    ac_od_id = int(ac_od_id.strip())

    plan = request.POST['plan']
    plan = int(plan.strip())

    record = OrderDetail.objects.get(ac_od_id=ac_od_id)

    record.plan = plan
    record.save()

    return HttpResponse(json.dumps(['ok']), mimetype='application/json')

def record_note(request):
    """
    record note by ac_od_id
    """
    ac_od_id =  request.POST['ac_od_id']
    ac_od_id = int(ac_od_id.strip())

    note = request.POST['note']

    record = OrderDetail.objects.get(ac_od_id=ac_od_id)

    record.production_note = note
    record.save()

    return HttpResponse(json.dumps(['ok']), mimetype='application/json')

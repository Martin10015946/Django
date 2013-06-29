import json
import urllib2
import urllib
from django.conf import settings
from production.models import OrderDetail, set_day_ETA
from django.conf import settings

def get_view_day(json_day):
    """
    Get an assembly list for the Timer.
    """
    assy_list = set_day_ETA(json_day)
    for od in assy_list:
        #check in local db if we have timed this od allready
        timed_od = OrderDetail.objects.filter(ac_od_id=od['ac_od_id'])
        timed_od = timed_od[0]
        if timed_od.start_time and timed_od.actual > 0: # update the assembly list
            od['start_time'] = timed_od.start_time
            od = timed_od.get_view_dict(od)
            od['class'] = 'product timed'
        else:
            od['class'] = 'product'
        od['plan'] = int(od['plan'])
    
    return assy_list

def update_play(data):
    p = OrderDetail.objects.get(ac_od_id=data['ac_od_id'])
    p.start_time = data['start_time']
    p.actual = 0
    p.pause = 0
    p.status=''
    p.save()
    return p

def update_record(data):
    p = OrderDetail.objects.get(ac_od_id=data['ac_od_id'])
    p.actual=data['actual']
    p.pause=data['pause']
    p.status=data['status']
    if data['status'] == 'ready': 
        p.assembled = 1
        access_post_data = [('id',data['ac_od_id']),('status','Ready')]
        result = urllib2.urlopen(settings.ACCESS_API_URL+'order_detail/update_status/', urllib.urlencode(access_post_data))        
    p.save()
    return p

def get_timed_product(fromday, endday, shop):
    """
    read the order detail from local db in the range of two given datetime objects
    """
    queryset = OrderDetail.objects.filter(shop=shop).filter(start_time__gte=fromday).filter(start_time__lte=endday)
    return queryset

def get_access_order(orders_object):
    """
    """
    ids = [od.ac_od_id for od in orders_object]
    url = settings.ACCESS_API_URL + 'order_details/'

    # do a post call to access_api
    param = urllib.urlencode({'ids':json.dumps(ids)})
    f = urllib2.urlopen(url,param)
    j = f.read()
    f.close()
    jrl = json.loads(j)

    return jrl
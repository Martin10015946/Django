import datetime
import json
import urllib2
from math import ceil
from collections import OrderedDict
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from production.models import OrderDetail
from supplies.models import Material, PlyStock
from supplies.models import get_week_plystock


def get_access_db_list(year, week_nr, shop):
    # TODO could be more generic - we use this in progress report as well
    url = '%sprogress_report/%s/%s/%s'%(settings.ACCESS_API_URL,year,week_nr,shop)
    f = urllib2.urlopen(url)
    j = f.read()
    f.close()
    return json.loads(j)

# TODO 
# the materials we are dealing with will be listed 
# in a client facing system at some point. For now
# they are just defined in dictionaries here in the 
# code.

def cores_shelf():
    return {1.5:0,4:0,6.5:0,12:0,18:0,24:0}

def finishes_shelf():
    return {'Walnut':0, 'Oak':0, 'White':0}

def specials_shelf():
    specials = OrderedDict()
    specials['Laminate'] = []
    specials['Lino'] = []
    specials['Special Orders'] = []
    specials['Paint'] = []
    specials['Compact'] = []
    return specials

def security():
    sec = {1.5:5,4:2,6.5:6,12:20,18:10,24:10}
    return sec

# TODO
# The suppliers will be defined in a table and manipulated
# in a client facing interface at some point. We define them
# here just as string repr. for now.

def get_supplier(s):
    d = {'Lino':'De Bruyn'}
    d['Paint'] = 'General Finishes'
    d['Laminate'] = 'Brent Plastic Ltd.'
    d['Compact 3'] = 'Brent Plastic Ltd.'
    if s in d:
        return d[s]
    else:
        return 'Supplier not recorded'

def sort_specials(od, specials):
    '''Put an order detail in the right special materials shelf.'''
    db_od = OrderDetail.objects.filter(ac_od_id=od['ac_od_id'])
    if db_od:
        if db_od[0].materials == None:
            db_od[0].materials = " "
        od['material']['order_qty'] = db_od[0].materials

    if od['material'] is None:
        specials['Special Orders'].append(od)
    elif od['material']['board'] == "Aeroply 1.5":
        pass
    elif od['material']['board'] == 'Compact 3':
        od['material']['supplier'] = get_supplier('Compact 3') 
        specials['Compact'].append(od)
    elif od['material']['board'] == 'Lino':
        od['material']['supplier'] = get_supplier('Lino') 
        specials['Lino'].append(od)
    elif od['material']['board'] == 'Paint':
        od['material']['supplier'] = get_supplier('Paint')
        specials['Paint'].append(od)
    elif od['material']['board'].startswith('Laminate') \
            or od['material']['board'].startswith('Colour'):
        od['material']['supplier'] = get_supplier('Laminate')
        specials['Laminate'].append(od)
    elif od['material']['board'].startswith('Raw'):
        pass
    else:
        specials['Special Orders'].append(od)

def sort_materials(week):
    cores = cores_shelf()
    finishes = finishes_shelf()
    specials = specials_shelf()

    for day in week:
        date = day.keys()[0]
        for od in day[date]:
            if od['material']:
                
                # assume no merging: all materials quantities are rounded up to 1 sheet
                qty = int(ceil(od['material']['materialqty']))

                # sort cores
                if od['material']['core'] in cores.keys():
                    cores[od['material']['core']] += qty

                # sort finishes
                if od['material']['finish'] in finishes.keys(): 
                    finishes[od['material']['finish']] += 2 * qty
                else: # take care of the special finishes
                    sort_specials(od, specials)

                od['material']['materialqty'] = round(od['material']['materialqty'],1)

            else: # if there is no materials then, assume it is special!
                sort_specials(od, specials)

    return week, cores, finishes, specials

def material_needs(request, year, week_nr):
    """List of all the material need to make one week."""
    week = get_access_db_list(year, int(week_nr), 'garage')
    week += get_access_db_list(year, int(week_nr), 'bricklane')
    week, week_cores, week_finishes, week_specials = sort_materials(week)
    data = {'week': week, 
            'week_cores': week_cores, 
            'week_finishes': week_finishes, 
            'week_specials': week_specials,
            'week_nr': week_nr,
            'ok_suppliers': ['Laminate','Lino','Paint','Compact']} # list of materials for which we display supplier name
    
    return render_to_response(
            'material_needs.html',
            data,
            context_instance=RequestContext(request))

def materials(request):
    """
    Order material in one click.

    Assume: it's monday morning.
    Assume: you are on time with lamination.
    
    This view will gather the materials you need to order for 
    the production of the next week. 
    
    You will then receive the material wednesday this week and start 
    using it on thursday.

    Also: you are ordering for two shops: garage and bricklane.
    """
    today = datetime.datetime.now()
    week_nr = int(today.strftime('%W'))+1
    year = today.strftime('%Y')
    
    # count the material need for the rest of this week (we have it in stock)
    # the rest of the week is wednesday, thursday and friday.
    this_week = get_access_db_list(year, week_nr,'garage')[2:]
    this_week += get_access_db_list(year, week_nr, 'bricklane')[2:]
    this_week, this_week_cores, this_week_finishes, this_week_specials = sort_materials(this_week) 

    # count the material need for next week (we need to order)
    next_week = get_access_db_list(year, week_nr+1, 'garage')
    next_week += get_access_db_list(year, week_nr+1, 'bricklane')
    next_week, next_week_cores, next_week_finishes, next_week_specials = sort_materials(next_week)

    # PLY
    # read the stock from PlyWood, if the the stock was recorded 
    # for the current week is passed to the template
    ply_stock = get_week_plystock(week_nr)
    # add up security, this week and next week cores in "totals"
    total = security()
    # merge total and ply_stock dictionary
    ret = {}
    for key, val in total.items():
        val += this_week_cores[key]
        val += next_week_cores[key]
        if key in ply_stock:
            ret[key] = [val, ply_stock[key]]
        else:
            ret[key] = [val, '']

    # SPECIALS
    if next_week_specials == specials_shelf(): 
        next_week_specials == None

    return render_to_response(
            'materials.html',{
                'total':ret
                ,'this_week_cores': this_week_cores
                ,'next_week_cores': next_week_cores
                ,'sec': security()
                ,'specials': next_week_specials 
                ,'home_on_server': settings.HOME_ON_SERVER
                ,'access_api_url': settings.ACCESS_API_URL
                }, context_instance=RequestContext(request))

def record_materials(request):
    """
    Update OrderDetail materials
    """
    if request.method == 'POST':
         # first occurence because the post pass a string and not an array
        json_value = request.POST.keys()[0]
        data = json.loads(json_value)

    p = OrderDetail.objects.get(ac_od_id=data['ac_od_id'])
    p.materials = data['materials']
    p.save()

    return HttpResponse(json.dumps(data['materials']), mimetype='application/json')

def stock_materials(request):
    other_materials = Material.objects.all().order_by('id')
    return render_to_response(
            'stock_materials.html',{
                'other_materials': other_materials
                ,'home_on_server' : settings.HOME_ON_SERVER
                ,'access_api_url' : settings.ACCESS_API_URL
                }, context_instance=RequestContext(request))

def record_stock(request):
    '''
    Record stock materials quantity (moslty layons). 
    Weekly check monthly order.
    '''
    if request.method == 'POST':
        json_value = request.POST.keys()[0] # first occurence because the post pass a string and not an array
        data = json.loads(json_value)

        data['week'] = int(data['week'])
        data['id'] = int(data['id'])
        if data['qty']:
            data['qty'] = int(data['qty'])
        else:
            data['qty'] = None

        material = Material.objects.get(id=data['id'])
        if data['week'] == 1:
            material.week1_qty = data['qty']
        elif data['week'] == 2:
            material.week2_qty = data['qty']
        elif data['week'] == 3:
            material.week3_qty = data['qty']
        elif data['week'] == 4:
            material.week4_qty = data['qty']
        elif data['week'] == 5:
            material.week5_qty = data['qty']
        material.save()

        return HttpResponse(json.dumps(data['id']), mimetype='application/json')

def record_stock_plywood(request):
    """
    Update plywood stock and record time of update
    """
    if request.method == 'POST':
        # clean up nominal thicknes form "\n" and spaces
        nominal_thickness = str(request.POST['nominal_thickness'].replace('\n','')).strip()
        p = PlyStock.objects.get(nominal_thickness=nominal_thickness)
        date = datetime.datetime.now()
        p.date_recorded = date
        p.stock_qty = int(request.POST['stock_qty'])
        p.save()

        return HttpResponse(json.dumps('ok'), mimetype='application/json')

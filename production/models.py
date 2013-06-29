from django.db import models
from django.conf import settings
import datetime, calendar
import ntpath

JS_TIME_FORMAT = '%Y/%m/%d %H:%M:%S'

class OrderDetail(models.Model):
    ac_od_id  = models.IntegerField() # MS Access Order Detail ID
    # Fields used in the Progress Report
    laminated = models.IntegerField(default=0)
    machined  = models.IntegerField(default=0)
    assembled = models.IntegerField(default=0)
    # Estimated Time of Arrival (Ready datetime) 
    eta = models.DateTimeField(null=True) 
    # We duplicate the following two informations from MS Access 
    # until we can make the rollovers query in access_api.
    shop = models.CharField(max_length=20, null=True)
    plan = models.IntegerField(null=True) 
    # Fields used in the Timer
    start_time = models.DateTimeField(null=True)
    actual = models.IntegerField(null=True)    
    pause = models.IntegerField(null=True)    
    status = models.CharField(max_length=20, null=True)  
    location = models.CharField(max_length=20, null=True)  
    materials = models.CharField(max_length=20, null=True)
    thickness = models.DecimalField(decimal_places=1, null=True, max_digits=18)
    fileprep = models.IntegerField(default=0, null=True) # NC file is prepared
    production_note = models.CharField(max_length=100, null=True)
    assembled_time = models.DateTimeField(null=True)

    def get_object_view(self):
        d = {'ac_od_id': self.ac_od_id}
        d['assembled'] = self.assembled
        if self.eta:
            d['eta'] = self.eta.strftime('%Y/%m/%d %H:%M:%S')
        d['plan'] = self.plan
        return d

    def get_view_dict(self, d):
        d['start_time'] = self.start_time.strftime(JS_TIME_FORMAT)
        d['actual'] = self.actual
        d['pause'] = self.pause
        d['total'] = self.actual + self.pause
        d['status'] = self.status
        return d


class RatReason(models.Model):
    MAYBECHOICE = (
        ('lamination', 'lamination'),
        ('machining', 'machining'),
        ('assembly', 'assembly'),
    )
    source = models.CharField(max_length=20, null=False, choices=MAYBECHOICE)
    reason = models.CharField(max_length=100, null=False)


class Rat(models.Model):
    ac_od_id = models.IntegerField() # MS Access Order Detail
    source = models.CharField(max_length=20, null=False)
    reason = models.CharField(max_length=100, null=False)
    date = models.DateTimeField(null=True)


class Preparation(models.Model):
    """
    Records preparation checks displayed on the landing page.
    """
    name = models.CharField(max_length=20, null=False)
    checked = models.IntegerField(default=0)
    when = models.DateTimeField(null=True) # when the box has been ticked

class Record(models.Model):
    """
    record rollover levels at regular intervals
    """
    date = models.DateTimeField(null=False, auto_now_add=True)
    rollovers = models.IntegerField(null=False)
    ready_to_machine = models.IntegerField(null=False)
    ready_to_assembly = models.IntegerField(null=False)
    shop = models.CharField(max_length=20, null=False)

class Jhistory(models.Model):
    """
    Record the machine job history log
    """
    shop = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    total_time = models.DateTimeField(null=True)
    machine_time = models.DateTimeField(null=True)
    start_type = models.CharField(max_length=100)
    end_type = models.CharField(max_length=100)
    connection = models.CharField(max_length=100)

    def get_view(self):
        name = ntpath.basename(self.name).replace('NEW.nc','')
        start_time = self.start_time.strftime('%Y/%m/%d %H:%M:%S')
        end_time = self.end_time.strftime('%Y/%m/%d %H:%M:%S')
        total_time = self.total_time.strftime('%H:%M')

        d = {
             'name': name
            ,'start_time' : start_time
            ,'end_time' : end_time
            ,'total_time' : total_time
        }

        return d

class Environment(models.Model):
    """
    Table of settings
    """
    MAYBECHOICE = (
        ('bricklane', 'Bricklane'),
        ('garage', 'Garage'),
        ('all_shops', 'All Shops'),
    )
    shop = models.CharField(max_length=20, choices=MAYBECHOICE)
    parameter_name = models.CharField(max_length=40)
    parameter_value = models.CharField(max_length=100)


def set_day_ETA(day):
    """
    Calculate when each order details of a day are going
    to be assembled.
    Each order detail is followed by a gap proportional
    to its length.
    """
    total_assembly = 0
    for d in day: total_assembly += d['plan']
    total_gap = settings.WORKING_DAY_MINUTES - total_assembly
    start = datetime.datetime.today()
    start = start.replace(hour=settings.WORKING_DAY_START_HR, minute=0, second=0)
    for od in day:
        plan = datetime.timedelta(minutes=od['plan'])
        eta = start + plan
        if od['plan'] !=0:
            gap = (float(od['plan'])/total_assembly) * total_gap
            start = eta + datetime.timedelta(minutes=gap)
        od['ETA'] = eta.strftime(JS_TIME_FORMAT)
    return day

def week_range(year, week):
    """
    get the year and the week number, for example 2013,8 and return a list of
    datetime objects, one for each day of the week
    """
    d = datetime.date(year, 1, 1)
    delta_days = d.isoweekday() - 1
    delta_weeks = week
    if year == d.isocalendar()[0]: delta_weeks -= 1
    start = d + datetime.timedelta(days=-delta_days, weeks=delta_weeks)
    r = [start]
    for i in range(1,7):
        r.append(start + datetime.timedelta(days=i))
    return r

def month_first_last(year,month):
    """
    returns datetime objects of the month
    """
    cal = calendar.Calendar()
    days = cal.itermonthdays(int(year), int(month))
    days = list(days)

    # removing zeroes from list
    while 0 in days: days.remove(0)

    month_day_list = []
    for day in days:
        day_string = year + '/' + str(month) + '/' + str(day)
        day_object = datetime.datetime.strptime(day_string, '%Y/%m/%d')
        month_day_list.append(day_object)

    return month_day_list

def record_status(data):
    """
    record the radio box of the landing page preparation
    """

    p = Preparation.objects.get(name=data['name'])

    p.name = data['name']
    p.when = data['when']
    p.checked = data['checked']
    p.save()

    return 'ok'


import datetime
from production.models import Jhistory, Environment
from django.conf import settings
from BeautifulSoup import BeautifulSoup

def get_log(shop, file_path, lines_number):

    log = open(file_path)
    records = log.readlines()
    last_records = records[-int(lines_number):]
    for line in last_records:

        el = BeautifulSoup(line)
        tag = el.find('job')
        name =  tag['name']
        start_time =  datetime.datetime.strptime(tag['starttime'], '%Y-%m-%d %H:%M:%S')
        end_time =  datetime.datetime.strptime(tag['endtime'], '%Y-%m-%d %H:%M:%S')

        # total time and machine time can have 3 formats: '%H:%M:%S', '%Y-%m-%d %H:%M:%S', ''
        if str(tag['totaltime']) != "":
            try:
                total_time =  datetime.datetime.strptime(tag['totaltime'], '%H:%M:%S')
            except:
                total_time =  datetime.datetime.strptime(tag['totaltime'], '%Y-%m-%d %H:%M:%S')

        if str(tag['machinetime']) != "":
            try:
                machine_time =  datetime.datetime.strptime(tag['machinetime'], '%H:%M:%S')
            except:
                machine_time =  datetime.datetime.strptime(tag['machinetime'], '%Y-%m-%d %H:%M:%S')

        start_type = tag['starttype']
        end_type = tag['endtype']
        connection = tag['connection']

        if int(machine_time.strftime('%M')) > settings.JOBHISTORY_MINIMUM_MINUTES:
            Jhistory.objects.get_or_create(shop=shop,
                                           name=name,
                                           start_time=start_time,
                                           end_time=end_time,
                                           total_time=total_time,
                                           machine_time=machine_time,
                                           start_type=start_type,
                                           end_type=end_type,
                                           connection=connection,
            )

def run():

    path_bricklane = Environment.objects.get(shop='bricklane', parameter_name='JOBHISTORY_PATH')
    lines_bricklane = Environment.objects.get(shop='bricklane', parameter_name='JOBHISTORY_LINES')

    path_garage = Environment.objects.get(shop='garage', parameter_name='JOBHISTORY_PATH')
    lines_garage = Environment.objects.get(shop='garage', parameter_name='JOBHISTORY_LINES')

    get_log('bricklane', path_bricklane.parameter_value, lines_bricklane.parameter_value)
    get_log('garage', path_garage.parameter_value, lines_garage.parameter_value)

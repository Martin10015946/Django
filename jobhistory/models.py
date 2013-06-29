from django.db import models
import datetime
from production.models import Jhistory, Environment
from django.conf import settings
from BeautifulSoup import BeautifulSoup

def get_log(shop, file_path, lines_number):

    """
    The server should be off. So, try to grab the log, if you can't don't give an exception.
    """

    try:

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
    except:
        # if the log isn't accessible go ahead
        pass


def update_job_history(shop):

    # the number of the last log's lines to read
    number_of_line = 5

    parameter = Environment.objects.get(shop=shop, parameter_name='JOBHISTORY_PATH')
    get_log(shop, parameter.parameter_value , number_of_line)

    return True
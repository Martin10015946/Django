import datetime
import calendar
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from production.models import Jhistory, week_range, month_first_last
from jobhistory.models import update_job_history

def month (request, year, month, shop):
    """ Machine job history of the month """

    month_days = month_first_last(year, month)
    counter = 0 # line counter
    days_job = []
    total_time_month_hours = 0
    total_time_month_minutes = 0

    for month_day in month_days:

        day = datetime.datetime.strftime(month_day, '%A %d %B')
        day_x_chart = datetime.datetime.strftime(month_day, '%A %d')

        javascript_day = datetime.datetime.strftime(month_day, '%Y/%m/%d')

        data = []
        total_time = datetime.timedelta()
        total_minutes_chart = 0
        jobs = Jhistory.objects.filter(shop=shop, start_time__year=month_day.year, start_time__month=month_day.month, start_time__day=month_day.day)
        for j in jobs:

            # retrieve formatted data from the model
            d = j.get_view()

            # compute total time
            hours = j.total_time.strftime('%H')
            minutes = j.total_time.strftime('%M')
            temp = datetime.timedelta(hours=int(hours),minutes=int(minutes))
            total_time = total_time + temp

            # increment time for chart column table
            total_minutes_chart += int(minutes)
            total_minutes_chart += int(hours) * 60

            # template table row index
            d['id'] = counter
            counter +=1

            data.append(d)

        total_time = str(total_time)[:4]

        ws_time = total_time.split(':')
        total_time_month_hours = total_time_month_hours + int(ws_time[0])
        total_time_month_minutes = total_time_month_minutes + int(ws_time[1])

        day_url = 'jobhistory' + '/' + month_day.strftime('%Y/%m/%d') + '/' + str(shop)


        days_job.append({'data': data,
                         'total_time': total_time,
                         'javascript_day': javascript_day,
                         'day': day,
                         'day_x_chart': day_x_chart,
                         'total_minutes_chart': total_minutes_chart,
                         'day_url': day_url
        })

    navigator = {}

    url_next = 'jobhistory/month' + '/' + year + '/' + str(int(month)+1) + '/' + shop
    navigator['url_next'] = url_next
    url_previous = 'jobhistory/month' + '/' + year + '/' + str(int(month)-1) + '/' + shop
    navigator['url_previous'] = url_previous

    this_month = datetime.datetime.today()
    this_month = this_month.strftime('%m')
    navigator['url_this_month'] = 'jobhistory/month' + '/' + year + '/' + this_month + '/' + shop

    view_month = datetime.datetime.strptime(month, '%m')
    view_month = view_month.strftime('%B')

    total_time_month_hours = total_time_month_hours + total_time_month_minutes/60
    total_time_month_minutes = total_time_month_minutes%60

    return render_to_response('job_history_month.html', {'data': days_job,
                                                         'navigator':navigator,
                                                         'shop': shop,
                                                         'month': view_month,
                                                         'total_month': {'total_time_month_hours':total_time_month_hours, 'total_time_month_minutes': total_time_month_minutes},
                                                         'home_on_server' : settings.HOME_ON_SERVER},
                                                    context_instance=RequestContext(request))

def week(request, year, week, shop):
    """ Machine job history of a week """
    w = week_range(int(year), int(week))

    # update jhistory table reading the log machine
    update_job_history(shop)

    days_job = []
    counter = 0 # line counter
    total_hours_week = 0
    total_minutes_week = 0

    for week_day in w:

        day = datetime.datetime.strftime(week_day, '%A %d %B')
        javascript_day = datetime.datetime.strftime(week_day, '%Y/%m/%d')

        data = []
        total_day_time = datetime.timedelta()

        jobs = Jhistory.objects.filter(shop=shop, start_time__year=week_day.year, start_time__month=week_day.month, start_time__day=week_day.day)

        for j in jobs:

            # retrieve formatted data from the model
            d = j.get_view()

            # increment total time per day
            hours = j.total_time.strftime('%H')
            minutes = j.total_time.strftime('%M')
            temp = datetime.timedelta(hours=int(hours),minutes=int(minutes))
            total_day_time = total_day_time + temp

            # template table row index
            d['id'] = counter
            counter +=1

            data.append(d)

        total_time = str(total_day_time)[:4]

        # retrieve the total time of the week
        ws_time = total_time.split(':')
        total_hours_week = total_hours_week + int(ws_time[0])
        total_minutes_week = total_minutes_week + int(ws_time[1])

        day_url = 'jobhistory' + '/' + week_day.strftime('%Y/%m/%d') + '/' + str(shop)

        days_job.append({'data': data, 'total_time': total_time, 'javascript_day': javascript_day, 'day': day, 'day_url': day_url})


    # total time of the week
    total_minutes = total_minutes_week%60
    total_hours = total_hours_week + total_minutes_week/60


    # navigation url
    navigator = {}
    today = datetime.datetime.today()
    today = today.strftime('%Y/%m/%d')
    url_today = 'jobhistory' + '/' + today + '/' + shop
    navigator['url_today'] = url_today

    url_next = 'jobhistory' + '/' + year + '/' + str(int(week) + 1) + '/' + shop
    navigator['url_next'] = url_next

    url_previous = 'jobhistory' + '/' + year + '/' + str(int(week) - 1) + '/' + shop
    navigator['url_previous'] = url_previous

    monday = w[0]
    monday = monday.strftime('%Y/%m/%d')
    url_monday = 'jobhistory' + '/' + monday + '/' + shop
    navigator['url_monday'] = url_monday

    url_week = 'jobhistory' + '/' + year + '/' + week + '/' + shop
    navigator['url_week'] = url_week

    # to retrieve the month take the first day of the week
    this_month = w[0].strftime('%m')
    navigator['url_this_month'] = 'jobhistory/month' + '/' + year + '/' + this_month + '/' + shop

    datapicker_day = datetime.datetime.today()
    datapicker_day = datapicker_day.strftime('%d/%m/%Y')

    return render_to_response('job_history_week.html', {'data': days_job,
                                                        'navigator':navigator,
                                                        'shop': shop,
                                                        'datapicker_day': datapicker_day,
                                                        'total_time': {'total_hours': total_hours, 'total_minutes': total_minutes},
                                                        'week': week,
                                                        'home_on_server' : settings.HOME_ON_SERVER},
                                                    context_instance=RequestContext(request))


def day(request, year, month, day, shop):
    """ Machine job history of a day """

    # update jhistory table reading the log machine
    update_job_history(shop)

    jobs = Jhistory.objects.filter(shop=shop, start_time__year=year, start_time__month=month, start_time__day=day)

    request_day = datetime.datetime.strptime(str(year) + '/' + str(month) + '/' + str(day), '%Y/%m/%d')
    day = datetime.datetime.strftime(request_day, '%A %d %B')
    javascript_day = datetime.datetime.strftime(request_day, '%Y/%m/%d')

    total_time = datetime.timedelta()

    data = []
    counter = 0
    for j in jobs:

        # retrieve formatted data from the model
        d = j.get_view()

        # compute total time
        hours = j.total_time.strftime('%H')
        minutes = j.total_time.strftime('%M')
        temp = datetime.timedelta(hours=int(hours),minutes=int(minutes))
        total_time = total_time + temp

        # template table row index
        d['id'] = counter
        counter +=1

        data.append(d)

    total_time = str(total_time)[:4]

    # navigation url
    navigator = {}
    today = datetime.datetime.today()
    today = today.strftime('%Y/%m/%d')
    url_today = 'jobhistory' + '/' + today + '/' + shop
    navigator['url_today'] = url_today

    previous = request_day - datetime.timedelta(days=1)
    previous = previous.strftime('%Y/%m/%d')
    url_previous = 'jobhistory' + '/' + previous + '/' + shop
    navigator['url_previous'] = url_previous

    next = request_day + datetime.timedelta(days=1)
    next = next.strftime('%Y/%m/%d')
    url_next = 'jobhistory' + '/' + next + '/' + shop
    navigator['url_next'] = url_next

    week = request_day.strftime('%U')
    week = int(week) + 1
    url_week = 'jobhistory' + '/' + year + '/' + str(week) + '/' + shop
    navigator['url_week'] = url_week

    this_month = request_day.strftime('%m')
    navigator['url_this_month'] = 'jobhistory/month' + '/' + year + '/' + this_month + '/' + shop

    datapicker_day = datetime.datetime.today()
    datapicker_day = datapicker_day.strftime('%d/%m/%Y')

    return render_to_response('job_history.html', {'jobs': data,
                                                   'day': day,
                                                   'datapicker_day': datapicker_day,
                                                   'shop': shop,
                                                   'javascript_day': javascript_day,
                                                   'total_time': total_time,
                                                   'navigator': navigator,
                                                   'home_on_server' : settings.HOME_ON_SERVER},
                                            context_instance=RequestContext(request))
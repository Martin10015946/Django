from django.conf.urls import patterns, include, url
import datetime
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',                      
    # landing page
    url(r'^$', 'production.views.dashboard'),
    url(r'^record_preparation', 'production.views.record_preparation'),
    
    # timer urls   
    url(r'^timer/(?P<shop>\w+)/$', 'utl_timer.views.today'),
    url(r'^timer_product/(?P<year>\d+)/(?P<week>\d+)/(?P<shop>\w+)/(?P<ac_od_id>\d+)/$', 'utl_timer.views.product'),
    url(r'^play/$', 'utl_timer.views.play'),
    url(r'^record/$', 'utl_timer.views.record'),
    url(r'^records/day/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/(?P<shop>\w+)/$', 'utl_timer.views.day'),
    url(r'^records/week/(?P<year>\d{4})/(?P<week>\d+)/(?P<shop>\w+)/$', 'utl_timer.views.week'),
    
    # progress report
    url(r'^progress_report/record_rat', 'progress_report.views.record_rat'),
    url(r'^progress_report/(?P<year>\d{4})/(?P<week_nr>\d+)/(?P<shop>\w+)/$', 'progress_report.views.index'),
    url(r'^progress_report/record$', 'progress_report.views.record'),
    url(r'^progress_report/rollovers/(?P<shop>\w+)/$', 'progress_report.views.rollovers'),
    url(r'^progress_report/record_plan', 'progress_report.models.record_plan'),
    url(r'^progress_report/record_note', 'progress_report.models.record_note'),
    url(r'^progress_report/order/(?P<order>\d{5})/$', 'progress_report.views.order'),
    url(r'^progress_report/noise/$', 'progress_report.views.noise'),
    url(r'^progress_report/inactive_orders/$', 'progress_report.views.inactive_orders'),
    url(r'^progress_report/inactive_orders/delete', 'progress_report.models.delete_orders_by_id'),
    url(r'^progress_report/inactive_orders/blank_future_eta', 'progress_report.models.blank_future_eta'),
    url(r'^progress_report/record_thickness', 'progress_report.views.record_thickness'),
    url(r'^progress_report/record_fileprep', 'progress_report.views.record_fileprep'),
    url(r'^progress_report/same_material/(?P<ac_od_id>\d+)/$', 'progress_report.views.same_material'),

    # materials
    url(r'^materials/$', 'supplies.views.materials'),
    url(r'^materials/(?P<year>\d{4})/(?P<week_nr>\d+)/$', 'supplies.views.material_needs'),
    url(r'^record_materials/$', 'supplies.views.record_materials'),
    url(r'^stock_materials/$', 'supplies.views.stock_materials'),
    url(r'^materials/record_stock', 'supplies.views.record_stock'),
    url(r'^record_stock_plywood', 'supplies.views.record_stock_plywood'),

    # delivery and pick ups
    url(r'^line_ups/$', 'progress_report.views.line_ups'),
    url(r'^landpage_line_ups/$', 'progress_report.views.landpage_line_ups'),
    url(r'^line_ups/record_location$', 'progress_report.views.record_location'),

    # board vision
    url(r'^boardvision/(?P<shop>\w+)/$', 'boardvision.views.index'),
    url(r'^boardvision/next_week/(?P<shop>\w+)/$', 'boardvision.views.index', {'folder':'next_week'}),
    url(r'^boardvision/set_status', 'boardvision.views.set_status'),

    # tool
    url(r'^tools/(?P<shop>\w+)/$', 'tools.views.index'),
    url(r'^tools/record_tool_value', 'tools.models.record_tool_value'),

    # tests
    url(r'^test/$', 'progress_report.views.test'),
    url(r'^pdf/$', 'progress_report.views.pdf'),

    # machine job history
    url(r'^jobhistory/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/(?P<shop>\w+)/$', 'jobhistory.views.day'),
    url(r'^jobhistory/(?P<year>\d{4})/(?P<week>\d+)/(?P<shop>\w+)/$', 'jobhistory.views.week'),
    url(r'^jobhistory/month/(?P<year>\d{4})/(?P<month>\d+)/(?P<shop>\w+)/$', 'jobhistory.views.month'),

    # admin
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)


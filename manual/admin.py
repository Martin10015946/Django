from django.contrib import admin
from models import ProgressReportTooltip
from models import ProgressLineUps

class ProgressReportAdmin(admin.ModelAdmin):
    list_display = ('anchor'
                    ,'explanation')

class ProgressLineUpsAdmin(admin.ModelAdmin):
    list_display = ('anchor'
                    ,'explanation')

admin.site.register(ProgressReportTooltip, ProgressReportAdmin)
admin.site.register(ProgressLineUps, ProgressLineUpsAdmin)

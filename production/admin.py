from django.contrib import admin
from models import Rat
from models import RatReason
from models import Preparation
from models import Environment

class RatAdmin(admin.ModelAdmin):
    list_display = ('ac_od_id',
                    'source',
                    'reason',)

class RatReasonAdmin(admin.ModelAdmin):
    list_display = ('source',
                    'reason',)
    list_filter = ('source',)

class PreparationAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'checked',
                    'when',)

class EnvironmentAdmin(admin.ModelAdmin):
    list_display = ('shop',
                    'parameter_name',
                    'parameter_value',)

admin.site.register(Preparation, PreparationAdmin)
admin.site.register(Rat, RatAdmin)
admin.site.register(RatReason, RatReasonAdmin)
admin.site.register(Environment, EnvironmentAdmin)

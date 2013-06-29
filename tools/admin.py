from django.contrib import admin
from models import Tool

class ToolAdmin(admin.ModelAdmin):
    list_display = ('shop'
                    ,'tool_number'
                    ,'tool_name'
                    ,'notes'
                    ,'measured_value'
                    ,'when_changed'
                    ,'max_use'
                    ,'standard_value'
    )

    list_filter = ('shop',)

admin.site.register(Tool, ToolAdmin)


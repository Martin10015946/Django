from django.contrib import admin
from models import Material

class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'note',
                    'monthly_qty',
                    'supplier',
                    'supplier_link',)

admin.site.register(Material, MaterialAdmin)
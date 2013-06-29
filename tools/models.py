import datetime
import json
from django.db import models
from django.http import HttpResponse

# Create your models here.
class Tool(models.Model):

    choices = (
        ('garage', 'garage'),
        ('bricklane', 'bricklane'),
    )

    shop = models.CharField(max_length=20, null=False, choices=choices)
    tool_number = models.IntegerField(null=False)
    tool_name = models.CharField(max_length=50, null=False)
    notes = models.CharField(max_length=100, null=True, blank=True)
    measured_value = models.DecimalField(decimal_places=2, null=False, max_digits=10)
    when_changed = models.DateTimeField(null=True)
    max_use = models.IntegerField(null=True)
    standard_value = models.DecimalField(decimal_places=2, null=False, max_digits=10)


    def get_days_used(self):
        '''return int nr of days = today - when_changed'''

        today = datetime.datetime.today().date()
        when_changed = self.when_changed.date()
        range = today - when_changed
        range = range.days

        return range

def get_tools_by_shop(shop):
    """
    get all the tools filtered by shop
    """
    tools = Tool.objects.filter(shop=shop).order_by('tool_number')
    for tool in tools:
        # retrieve range of days used
        days_used = tool.get_days_used()
        tool.days_used = days_used

        # format datetime when_changed form the template
        formatted_date = tool.when_changed.strftime('%d/%m/%Y')
        tool.formatted_date = formatted_date

        # whether the tool is expired or not
        if tool.max_use:
            if int(days_used) > tool.max_use:
                tool.expired = True
            else:
                tool.expired = False
        else:
            tool.expired = False


    return tools

def record_tool_value(request):
    """ Ajax call """

    if request.POST:
        tool_number = int(request.POST['tool_number'])
        value = float(request.POST['value'])
        shop = request.POST['shop']
    else:
        return False

    today = datetime.datetime.today()

    tool = Tool.objects.get(tool_number=tool_number, shop=shop)
    tool.measured_value = value
    tool.when_changed = today
    tool.save()

    result = {'measured_value': float(tool.measured_value), 'standard_value': float(tool.standard_value)}

    # this function returns the standard value
    return HttpResponse(json.dumps(result), mimetype='application/json')

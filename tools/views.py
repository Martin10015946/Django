from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.contrib.sites.models import Site
from tools.models import get_tools_by_shop

def index(request, shop):

    tools = get_tools_by_shop(shop)

    return render_to_response(
                'tools.html', {
                     'home_on_server' : settings.HOME_ON_SERVER
                    ,'tools' : tools
                    ,'shop' : shop
                } , context_instance=RequestContext(request))
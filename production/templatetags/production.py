from django import template

register = template.Library()

@register.filter
def shortshop(shop):
    if shop == 'Bricklane': return 'BL'
    elif shop == 'Battersea': return 'GR'
    else: return shop

@register.filter
def display_hours(minutes):
    if minutes >= 0:
        minutes = int(minutes) 
        sign = 1
    else:
        minutes = int(minutes) * -1
        sign = -1

    hours, minutes = divmod(minutes, 60)
    
    if hours <= 9: h='0%s'
    else: h='%s'
    if minutes <= 9: m='0%s'
    else: m='%s'
    
    if sign == 1:
        return (h+':'+m)%(hours, minutes)
    else:
        return ('-'+h+':'+m)%(hours, minutes)

@register.filter
def files_weekday(value):
    # counter starts at 1
    # and first are files 0
    l = ['','Rollovers']
    l.append('Monday')
    l.append('Tuesday')
    l.append('Wednesday')
    l.append('Thursday')
    l.append('Friday')
    l.append('Saturday')
    l.append('Sunday')
    return l[value]
    

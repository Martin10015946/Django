import datetime
from production.models import Record
from progress_report.models import get_rollovers_total, get_assembly_buffer
from boardvision.views import get_ncfolder_path, get_view_days


def run():
    record_data_by_shop('garage')
    record_data_by_shop('bricklane')

def record_data_by_shop(shop):
    """
    insert in Record table the total of assembly and rollover
    """
    rollovers = Record()
    rollovers.date = datetime.datetime.today()
    rollovers.rollovers = get_rollovers_total(shop)
    rollovers.ready_to_assembly = get_assembly_buffer(shop)
    rollovers.shop = shop

    # if it cant handle the path set to 0 (Nello computer)
    try:
        path = get_ncfolder_path(shop, 'this_week')
        x, y, ready_to_machine = get_view_days(path)
        rollovers.ready_to_machine = ready_to_machine
    except:
        rollovers.ready_to_machine = 0

    rollovers.save();

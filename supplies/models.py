from django.db import models

class Material(models.Model):
    name = models.CharField(max_length=100, null=False)
    note = models.TextField(null=True)
    monthly_qty = models.IntegerField(null=True)
    week1_qty = models.IntegerField(null=True, blank=True)
    week2_qty = models.IntegerField(null=True, blank=True)
    week3_qty = models.IntegerField(null=True, blank=True)
    week4_qty = models.IntegerField(null=True, blank=True)
    week5_qty = models.IntegerField(null=True, blank=True)
    supplier = models.CharField(max_length=100, null=True)
    supplier_link = models.CharField(max_length=100, null=True, blank=True)


class PlyStock(models.Model):
    """
    Record Plywood stock for each thickness and 
    record when the stock has been updated.
    """
    nominal_thickness = models.CharField(max_length=20, null=True)
    stock_qty = models.IntegerField(default=0, null=True)
    date_recorded = models.DateTimeField(null=True)

    def nominal_as_float(self):
        return float(self.nominal_thickness.replace('mm','').strip())

def get_week_plystock(week_now):
    stock = PlyStock.objects.all()
    ret = {}
    for element in stock:
        if element.date_recorded:
            week_recorded = int(element.date_recorded.strftime('%W'))+1
            if week_recorded == week_now: 
                ret[element.nominal_as_float()] = element.stock_qty
    return ret

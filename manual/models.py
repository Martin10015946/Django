from django.db import models

class ProgressReportTooltip(models.Model):
    anchor = models.CharField(max_length=100) 
    explanation = models.TextField(null=True)
    
class ProgressLineUps(models.Model):
    anchor = models.CharField(max_length=100)
    explanation = models.TextField(null=True)


def get_pr_tooltips():
    prt = ProgressReportTooltip.objects.all()
    rd = {}
    for o in prt: rd[o.anchor] = o.explanation
    return rd 

def get_lu_tooltips():
    prt = ProgressLineUps.objects.all()
    rd = {}
    for o in prt: rd[o.anchor] = o.explanation
    return rd

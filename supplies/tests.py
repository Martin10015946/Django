"""
Run tests with "manage.py test".
Or "manage.py test supplies", to run just the tests below.

I'm using this : http://toastdriven.com/blog/2011/apr/10/guide-to-testing-in-django/
as a manual.

I have run this command:

`python manage.py dumpdata supplies --indent=4 > supplies/fixtures/supplies_views_testdata.json`

to create test fixtures.
"""

import urllib2
import json
from django.test import TestCase
from models import PlyStock, get_week_plystock
import views


class PlyStockModelTest(TestCase):
    fixtures = ['supplies_views_testdata.json']

    def test_nominal_as_float(self):
        ps = PlyStock.objects.get(nominal_thickness="12 mm")
        self.assertEqual(ps.nominal_as_float(), 12.0)

    def test_get_week_plystock(self):
        self.assertEqual(get_week_plystock(24)[6.5], 12)


class SuppliesURLs(TestCase):
    fixtures = ['supplies_views_testdata.json']

    def test_one_click_order(self):
        resp = self.client.get('/materials/')
        self.assertEqual(resp.status_code, 200)

    def test_material_needs_week(self):
        resp = self.client.get('/materials/2013/25/')
        self.assertEqual(resp.status_code, 200)

    def test_stock_materials(self):
        resp = self.client.get('/stock_materials/')
        self.assertEqual(resp.status_code, 200)

    def test_record_stock_plywood(self):
        data = {'nominal_thickness': '12 mm', 'stock_qty':'5'}
        resp = self.client.post('/record_stock_plywood', data)
        self.assertEqual(resp.status_code, 200)
        ps = PlyStock.objects.get(nominal_thickness='12 mm')
        self.assertEqual(ps.nominal_as_float(), 12.0)
        self.assertEqual(ps.stock_qty, 5)


class MaterialSorting(TestCase):

    def progress_report_fix(self, s):
        # Shortcut for non-ORM fixtures
        url = 'http://169.254.184.4/production/static/json/' + s
        f = urllib2.urlopen(url)
        j = f.read()
        f.close()
        return json.loads(j)

    def test_sort_materials(self):
        week = self.progress_report_fix('progress_report_BL.json')
        week += self.progress_report_fix('progress_report_GR.json')
        week, cores, finishes, specials = views.sort_materials(week)
        cores_expect = {1.5: 1, 6.5: 1, 4: 0, 12: 40, 18:31, 24:16}
        # Test cores sorting
        self.assertEqual(cores, cores_expect)
        # Test special finishes sorting
        self.assertEqual(len(specials['Laminate']), 3)
        self.assertEqual(len(specials['Lino']), 1)
        self.assertEqual(specials['Lino'][0]['ac_o_id'], 33974)

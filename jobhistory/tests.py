from django.test import TestCase

from models import Jhistory

class TestJobhistoryUrl(TestCase):
    """
    testing the urls
    """
    def testMonthViewUrl(self):
        resp = self.client.get('/jobhistory/month/2013/03/bricklane/')
        self.assertEqual(resp.status_code, 200)

    def testWeekViewUrl(self):
        resp = self.client.get('/jobhistory/2013/6/bricklane/')
        self.assertEqual(resp.status_code, 200)

    def testDayViewUrl(self):
        resp = self.client.get('/jobhistory/2013/03/01/bricklane/')
        self.assertEqual(resp.status_code, 200)

class TestTemplate(TestCase):
    """
    testing the template variables
    """
    def testMonthViewTemplate(self):
        resp = self.client.get('/jobhistory/month/2013/03/bricklane/')
        self.assertTrue('data' in resp.context)

    def testWeekViewTemplate(self):
        resp = self.client.get('/jobhistory/2013/6/bricklane/')
        self.assertTrue('data' in resp.context)

    def testDayViewTemplate(self):
        resp = self.client.get('/jobhistory/2013/03/01/bricklane/')
        self.assertTrue('jobs' in resp.context)

class TestModel(TestCase):
    """
    testing the model
    """
    def setUp(self):
        Jhistory.objects.create(shop='Test', name='bla bla')

    def testJobhistoryModel(self):
        jh = Jhistory.objects.get(shop='Test')
        self.assertEqual(jh.shop,'Test')
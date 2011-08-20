import unittest

from django.db import models as django_models

from admin_stats import admin, models
from admin_stats.templatetags import admin_stats_tags

class AdminStatsTestModel(django_models.Model):
    value = django_models.IntegerField()
    
    def __unicode__(self):
        return unicode(self.value)


class AdminStatsTestMixin(object):
    """
    Mixin for tests.
    """
    def create_instances(self, *args):
        instances = []
        for value in args:
            instances.append(AdminStatsTestModel.objects.create(value=value))
        return instances

    def all(self):
        return AdminStatsTestModel.objects.all()

    def clean(self):
        AdminStatsTestModel.objects.all().delete()

    def get_stats(self):
        return (
            models.Avg('value'), 
            models.Sum('value'), 
            models.Min('value', alone=True),
            models.Max('value'),
            self.dummy(),
        )

    def dummy(self):
        return lambda request, queryset, data: (u'answer', 42)


class ModelTestCase(unittest.TestCase, AdminStatsTestMixin):
    def setUp(self):
        self.create_instances(1, 3, 5, 8, 13)

    def test_aggregates(self):
        stats = avg, sum_, min_, max_, dummy = self.get_stats()
        aggregates = models.collect_aggregates(stats)
        self.assertEqual([type(i) for i in aggregates], 
            [django_models.Avg, django_models.Sum, django_models.Max])
        
        queryset = self.all()
        data = models.aggregate(queryset, aggregates)
        self.assertEqual(data['value__avg'], 6.0)
        self.assertEqual(data['value__sum'], 30)
        self.assertEqual(data['value__max'], 13)

        expected_results = [
            (u'Average value', 6.0), 
            (u'Total value', 30), 
            (u'Min value', 1), 
            (u'Max value', 13), 
            ('answer', 42),
        ]
        results = [i(None, queryset, data) for i in stats]
        self.assertEqual([tuple(i) for i in results], expected_results)
        
    def tearDown(self):
        self.clean()

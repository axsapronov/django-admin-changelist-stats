from django.db import models
from django.utils.translation import ugettext_lazy as _

class BaseAggregation(object):
    """
    Base class for aggregation stats.
    Subclasses likely will override the *get_value* and *get_label* methods
    and will define an *_aggregates* attribute.
    """
    label = None
    _aggregates = []

    def __init__(self, field, alone=False):
        self.field = field
        self.alone = alone
    
    def get_aggregates(self):
        return [i(self.field) for i in self._aggregates]

    def __call__(self, request, queryset, data):
        """
        The base aggregator instances are callbles, like any other stats
        object.
        """
        self.request = request
        self.queryset = queryset
        if self.alone:
            data = queryset.aggregate(*self.get_aggregates())
        self.data = data
        return self.get_label(), self.get_value()

    def get_value(self):
        """
        Must return the value of this stat.
        """
        raise NotImplementedError

    def get_label(self):
        """
        Return the label for this stat.
        """
        opts = self.queryset.model._meta
        return u'%s %s' % (self.label, opts.get_field(self.field).verbose_name)


class Avg(BaseAggregation):
    """
    Average value for the given field.
    """
    _aggregates = [models.Avg]
    label = _('Average')

    def get_value(self):
        return self.data['%s__avg' % self.field]


class Sum(BaseAggregation):
    """
    Total value for the given field.
    """
    _aggregates = [models.Sum]
    label = _('Total')

    def get_value(self):
        return self.data['%s__sum' % self.field]


class Min(BaseAggregation):
    """
    Min value for the given field.
    """
    _aggregates = [models.Min]
    label = _('Min')

    def get_value(self):
        return self.data['%s__min' % self.field]


class Max(BaseAggregation):
    """
    Max value for the given field.
    """
    _aggregates = [models.Max]
    label = _('Max')

    def get_value(self):
        return self.data['%s__max' % self.field]


def collect_aggregates(stats):
    """
    Collects all aggregates used by *stats* callables
    in order to minimize db queries.
    """
    aggregates = []
    for i in stats:
        if hasattr(i, 'alone') and not i.alone:
            aggregates.extend(i.get_aggregates())
    return aggregates


def aggregate(queryset, aggregates):
    """
    Return the aggregated data using *aggregates* over *queryset*.
    """
    return queryset.aggregate(*aggregates) if aggregates else {}

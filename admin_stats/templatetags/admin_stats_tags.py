# -*- coding: utf-8 -*-
import re

from django import template
from django.db.models import Avg, Sum, Min, Max, Count

from admin_stats import models

register = template.Library()

COLLECT_STATS_PATTERN = r'^for\s+(?P<cl>[\w\.]+)\s+as\s+(?P<var_name>\w+)'
COLLECT_STATS_EXPRESSION = re.compile(COLLECT_STATS_PATTERN)


@register.tag
def collect_stats(parser, token):
    """
    Usage:

    .. code-block:: html+django
    
        {% collect_stats for cl as varname %}
    
    After this call, in the template context a *varname* variable will
    contain all the stats about *cl* admin changelist as an iterator 
    returning *(label, value)* tuples.
    """
    # args validation
    try:
        tag_name, tag_args = token.contents.split(None, 1)
    except ValueError:
        message = "%r tag requires arguments" % token.contents.split()[0]
        raise template.TemplateSyntaxError(message)

        # use regexp to catch args
    match = COLLECT_STATS_EXPRESSION.match(tag_args)
    if match is None:
        message = "Invalid arguments for %r tag" % token.contents.split()[0]
        raise template.TemplateSyntaxError(message)

    # call the node
    return CollectStatsNode(*match.groups())


class CollectStatsNode(template.Node):
    """
    Insert into context the stats for the current queryset.
    """

    def __init__(self, cl, varname):
        self.cl = template.Variable(cl)
        self.varname = varname

    def render(self, context):
        # retreiving queryset from admin changelist
        cl = self.cl.resolve(context)
        objects = cl.result_list
        # getting request
        request = context['request']
        # getting stats callables
        callables = cl.model_admin.get_stats(request, objects)
        # getting aggregates (to avoid too many db queries)
        aggregates = models.collect_aggregates(callables)
        # hit the db for aggregated data
        data = models.aggregate(objects, aggregates)
        # calling all stats callbales
        context[self.varname] = [i(request, objects, data) for i in callables]
        return u''


# UTILITY FILTERS (actually not used by the app)

def _get_aggregation_filter(func):
    """
    This is a filter factory that creates the following filters:
        - avg_of
        - sum_of
        - min_of
        - max_of
        - count_of
    Each one is used over a queryset and return the aggregation of
    the given field, e.g.:

    .. code-block:: html+django

        {{ myqueriset|avg_of:'field' }}
    """

    def aggregation_filter(queryset, field):
        aggregations = queryset.aggregate(aggregated=func(field))
        return aggregations['aggregated']

    return aggregation_filter


for func in Avg, Sum, Min, Max, Count:
    filter_name = '%s_of' % (func.name.lower())
    register.filter(name=filter_name)(_get_aggregation_filter(func))

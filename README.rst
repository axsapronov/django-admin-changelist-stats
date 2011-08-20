This simple application provides stats and aggregation capabilities for the 
Django admin changelist view.

It allows to display stats at the end of the changelist page in a easy way,
just adding one option to the model admin object.


Installation
~~~~~~~~~~~~

The Mercurial repository of the application can be cloned with this command::

    hg clone https://bitbucket.org/frankban/django-admin-changelist-stats

The ``admin_stats`` package, included in the distribution, should be
placed on the ``PYTHONPATH``.

Otherwise you can just ``pip install django-admin-changelist-stats``.


Settings
~~~~~~~~
    
Add ``'admin_stats'`` to the ``INSTALLED_APPS`` in your *settings.py*.


Quickstart
~~~~~~~~~~

Assume you have a *Vote* model with a score integer field.
The related model admin would look like this::

    from django.contrib import admin

    from myproject.vote import models

    class VoteAdmin(admin.ModelAdmin):
        list_display = ('__unicode__',)

    admin.site.register(models.Vote, VoteAdmin)

It is straightforward to display simple aggregation stats at the end of the
changelist page. For instance, if you want to display the average score and
the sum of all scores, referred to the votes currently present in the view,
you can just write::

    from admin_stats.admin import StatsAdmin, Avg, Sum

    class VoteAdmin(StatsAdmin):
        list_display = ('__unicode__',)
        stats = (Avg('score'), Sum('score'))

Note that now the model admin is a subclass of *StatsAdmin*.


Builtin stats
~~~~~~~~~~~~~

The application provides the following aggregation stats: 
    
    - *Avg*: the average of values over the results
    - *Sum*: the total sum of values
    - *Min*: the min value over the queryset
    - *Max*: the max value

Each one takes the related field as arguments, as seen in the example above.
To avoid too many db queries, the aggregation is done using a single
*queryset.aggregate* call, but, if you want, you can hit the database all 
the times you want using the *alone* kwarg, e.g.::

    stats = (Avg('score'), Sum('score'), Min('score', alone=True))


Custom stats
~~~~~~~~~~~~

The *stats* admin option takes a sequence of callables, and obviously you
can write your own.
A stats callable takes 3 arguments:

    - the current *request*
    - the current *objects* displayed in the changelist page
    - a dict object *data* (the result of all collected aggregations)

and must return a sequence *(label, value)* where the label is a 
short description of the value returned, e.g.::

    def answer(request, objects, data):
        return 'The Answer', 42

    class VoteAdmin(StatsAdmin):
        stats = [answer]

The *value* returned by custom stats is considered safe, so it can be an
html string too.

from django.contrib import admin

from admin_stats.models import Avg, Sum, Min, Max

class StatsAdmin(admin.ModelAdmin):
    """
    Base model admin for stats.
    """
    change_list_template = 'admin_stats/change_list.html'
    stats = None

    def get_stats(self, request, queryset):
        from django.contrib.admin.views.main import IS_POPUP_VAR
        if self.stats is None or IS_POPUP_VAR in request.GET:
            return []
        return self.stats

from django.contrib import admin
from django.contrib.admin import ModelAdmin
from martor.widgets import AdminMartorWidget

from apps.staff.models import *


@admin.register(Team)
class TeamAdmin(ModelAdmin):
    list_display = ['title_fa']
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }
    pass


@admin.register(Staff)
class StaffAdmin(ModelAdmin):
    list_display = ['name_fa']

    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }


from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.db import models
from django.core.exceptions import ValidationError

from martor.widgets import AdminMartorWidget

from .models import Intro, TimelineEvent, Prize, Stat, Count, Timer


@admin.register(Intro)
class IntroAdmin(ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }


@admin.register(TimelineEvent)
class TimelineEventAdmin(ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }


@admin.register(Prize)
class PrizeAdmin(ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }


@admin.register(Stat)
class StatAdmin(ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }


@admin.register(Count)
class CountAdmin(ModelAdmin):
    list_display = ['title', 'app_name', 'model_name', 'get_count', 'show']
    list_editable = ['show']
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }


@admin.register(Timer)
class TimerAdmin(ModelAdmin):
    list_display = ['title', 'time']

    def save_model(self, request, obj, form, change):
        if Timer.objects.count() > 0:
            raise ValidationError('There must be only one timer')
        super(TimerAdmin, self).save_model(request, obj, form, change)

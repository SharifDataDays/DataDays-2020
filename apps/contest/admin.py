from django.contrib import admin
from django.db import models
from martor.widgets import AdminMartorWidget

from . import models as contest_models


# Register your models here.

class QuestionRecipeInline(admin.StackedInline):
    model = contest_models.QuestionRecipe


@admin.register(contest_models.Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ['title']


@admin.register(contest_models.Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ['title']


@admin.register(contest_models.Task)
class TaskAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }


@admin.register(contest_models.Trial)
class TrialAdmin(admin.ModelAdmin):
    pass


@admin.register(contest_models.TrialRecipe)
class TrialRecipeAdmin(admin.ModelAdmin):
    inlines = [QuestionRecipeInline]


@admin.register(contest_models.QuestionRecipe)
class QuestionRecipeAdmin(admin.ModelAdmin):
    pass


@admin.register(contest_models.UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    pass

from django.contrib import admin
from django.db import models
from martor.widgets import AdminMartorWidget

from . import models as contest_models


# Register your models here.

class TeamTaskInline(admin.StackedInline):
    model = contest_models.TeamTask


class QuestionRecipeInline(admin.StackedInline):
    model = contest_models.QuestionRecipe


class MilestoneInline(admin.StackedInline):
    model = contest_models.Milestone


class TaskInline(admin.StackedInline):
    model = contest_models.Task


class TrialRecipeInline(admin.StackedInline):
    model = contest_models.TrialRecipe


class QuestionSubmissionInline(admin.StackedInline):
    model = contest_models.QuestionSubmission


class TrialInline(admin.StackedInline):
    model = contest_models.Trial


@admin.register(contest_models.Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'start_date', 'end_date']
    list_editable = ['title', 'start_date', 'end_date']
    sortable_by = ['title', 'start_date', 'end_date']
    list_filter = ['start_date', 'end_date']
    inlines = [MilestoneInline]


@admin.register(contest_models.Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'start_date', 'end_date', 'team_size']
    list_editable = ['title', 'start_date', 'end_date', 'team_size']
    sortable_by = ['title', 'start_date', 'end_date']
    list_filter = ['start_date', 'end_date', 'team_size']
    inlines = [TaskInline]


@admin.register(contest_models.Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'topic', 'trial_cooldown', 'max_trials_count']
    list_editable = ['topic', 'trial_cooldown', 'max_trials_count']
    sortable_by = ['topic', 'trial_cooldown', 'max_trials_count']
    list_filter = ['trial_cooldown', 'max_trials_count']
    inlines = [TrialRecipeInline]


@admin.register(contest_models.TeamTask)
class TeamTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'content_finished', 'last_trial_time']
    list_editable = ['content_finished']
    list_filter = ['content_finished']
    inlines = [TrialInline]


@admin.register(contest_models.Trial)
class TrialAdmin(admin.ModelAdmin):
    list_display = ['id', 'score', 'due_time', 'start_time', 'submit_time']
    list_editable = ['score']
    search_fields = ['score']
    sortable_by = ['score', 'start_time', 'submit_time']
    inlines = [QuestionSubmissionInline]


@admin.register(contest_models.TrialRecipe)
class TrialRecipeAdmin(admin.ModelAdmin):
    inlines = [QuestionRecipeInline]


@admin.register(contest_models.QuestionRecipe)
class QuestionRecipeAdmin(admin.ModelAdmin):
    list_display = ['id', 'question_type', 'priority', 'count']
    list_editable = ['question_type', 'priority', 'count']
    list_filter = ['question_type']
    sortable_by = ['priority', 'count']


@admin.register(contest_models.QuestionSubmission)
class QuestionSubmissionAdmin(admin.ModelAdmin):
    list_display = ['answer', 'score']
    list_editable = ['score']
    sortable_by = ['score']

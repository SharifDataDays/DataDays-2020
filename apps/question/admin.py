from django.contrib import admin
from django.db import models
from django import forms

from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin
from martor.widgets import AdminMartorWidget
from django_ace import AceWidget

from . import models as question_models


class ChoicesInline(admin.StackedInline):
    model = question_models.Choices
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }


class FilesInline(admin.StackedInline):
    model = question_models.NeededFilesForQuestionJudgment


class CommonAdminFeatures(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
        models.CharField: {'widget': AceWidget(mode='python')}
    }
    readonly_fields = ['type', 'judge_function_name']
    list_display = ['id', '__str__', 'max_score', 'type']
    list_display_links = ['__str__', 'id']
    list_editable = ['max_score']
    sortable_by = ['id', 'max_score']
    search_fields = ['max_score']


@admin.register(question_models.Question)
class QuestionAdmin(PolymorphicParentModelAdmin, CommonAdminFeatures):
    inlines = [FilesInline]
    base_model = question_models.Question

    child_models = [question_models.SingleAnswer, question_models.MultiAnswer,
                    question_models.SingleSelect, question_models.MultiSelect,
                    question_models.FileUpload, question_models.ManualJudgment,
                    question_models.NumericRange
                    ]
    list_filter = ['type', 'max_score']

    def has_add_permission(self, request):
        return False


@admin.register(question_models.SingleAnswer)
class SingleAnswerAdmin(PolymorphicChildModelAdmin, CommonAdminFeatures):
    inlines = [FilesInline]
    base_model = question_models.Question
    show_in_index = True


@admin.register(question_models.MultiAnswer)
class MultiAnswerAdmin(PolymorphicChildModelAdmin, CommonAdminFeatures):
    inlines = [FilesInline]
    base_model = question_models.Question
    show_in_index = True


@admin.register(question_models.SingleSelect)
class SingleSelectAdmin(PolymorphicChildModelAdmin, CommonAdminFeatures):
    inlines = [ChoicesInline, FilesInline]
    base_model = question_models.Question
    show_in_index = True


@admin.register(question_models.MultiSelect)
class MultiSelectAdmin(PolymorphicChildModelAdmin, CommonAdminFeatures):
    inlines = [ChoicesInline, FilesInline]
    base_model = question_models.Question
    show_in_index = True


@admin.register(question_models.FileUpload)
class FileUploadAdmin(PolymorphicChildModelAdmin, CommonAdminFeatures):
    inlines = [FilesInline]
    base_model = question_models.Question
    show_in_index = True


@admin.register(question_models.NumericRange)
class NumericRangeAdmin(PolymorphicChildModelAdmin, CommonAdminFeatures):
    inlines = [FilesInline]
    base_model = question_models.Question
    show_in_index = True

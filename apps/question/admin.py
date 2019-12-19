from django.contrib import admin
from django.db import models

from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin
from martor.widgets import AdminMartorWidget

from . import models as question_models


# Register your models here.

class Choices(admin.StackedInline):
    model = question_models.Choices
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }


class CommonAdminFeatures(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }
    readonly_fields = ['type']
    list_display = ['id', '__str__', 'max_score', 'topic', 'type']
    list_display_links = ['__str__', 'id']
    list_editable = ['topic', 'max_score']
    sortable_by = ['id', 'max_score', 'topic']
    search_fields = ['topic', 'max_score']


@admin.register(question_models.Question)
class QuestionAdmin(PolymorphicParentModelAdmin, CommonAdminFeatures):
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
    base_model = question_models.Question
    show_in_index = True


@admin.register(question_models.MultiAnswer)
class MultiAnswerAdmin(PolymorphicChildModelAdmin, CommonAdminFeatures):
    base_model = question_models.Question
    show_in_index = True


@admin.register(question_models.SingleSelect)
class SingleSelectAdmin(PolymorphicChildModelAdmin, CommonAdminFeatures):
    inlines = [Choices]
    base_model = question_models.Question
    show_in_index = True


@admin.register(question_models.MultiSelect)
class MultiSelectAdmin(PolymorphicChildModelAdmin, CommonAdminFeatures):
    inlines = [Choices]
    base_model = question_models.Question
    show_in_index = True


@admin.register(question_models.FileUpload)
class FileUploadAdmin(PolymorphicChildModelAdmin, CommonAdminFeatures):
    base_model = question_models.Question
    show_in_index = True


@admin.register(question_models.NumericRange)
class NumericRangeAdmin(PolymorphicChildModelAdmin, CommonAdminFeatures):
    base_model = question_models.Question
    show_in_index = True

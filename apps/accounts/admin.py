import csv

from django.http import HttpResponse
from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode

from apps.accounts.models import \
    University, Profile, ResetPasswordToken, ActivateUserToken


class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = \
            'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow(
                [getattr(obj, field) for field in field_names]
            )

        return response

    export_as_csv.short_description = "Export Selected"


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin, ExportCsvMixin):
    search_fields = [
        'firstname_fa',
        'firstname_en',
        'lastname_fa',
        'lastname_en',
        'birth_date',
        'university',
        'uni__name',
        'major',
        'bmp',
        'user__username',
    ]
    list_display = [
        'firstname_en',
        'lastname_en',
        'birth_date',
        'university',
        'uni',
        'major',
        'bmp',
    ]

    actions = ['export_as_csv']


@admin.register(ResetPasswordToken)
class ResetPasswordTokenAdmin(admin.ModelAdmin):
    def username(self, obj):
        try:
            uid = urlsafe_base64_decode(obj.uid).decode('utf-8')
            qs = User.objects.filter(id=uid)
            if qs.count() == 1:
                return qs.get().username
        except Exception:
            pass
        return "SHIT REPORT THIS TO TECH-ADMIN"

    list_display = ['username']


@admin.register(ActivateUserToken)
class ActivateUserTokenAdmin(admin.ModelAdmin):
    def username(self, obj):
        try:
            email = urlsafe_base64_decode(obj.eid).decode('utf-8')
            qs = User.objects.filter(email=email)
            if qs.count() == 1:
                return qs.get().username
        except Exception:
            pass
        return "SHIT REPORT THIS TO TECH-ADMIN"

    list_display = ['username']

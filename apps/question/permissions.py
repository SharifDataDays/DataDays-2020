from rest_framework import permissions


class HasStaffAccessToQuestions(permissions.BasePermission):

    def has_permission(self, request, view):
        for group in request.user.groups.all():
            permissions = group.permissions.all()
            codes = [p.codename for p in permissions]
            if 'add_question' in codes and 'change_question' in codes:
                return True
        if request.user.is_superuser:
            return True
        return False


from rest_framework.permissions import BasePermission
from .models import Organisation, User

class BelongsToOrg(BasePermission):
    def has_permission(self, request, orgId, view):
        org = Organisation.objects.get(orgId=orgId, users=User.objects.get(
            id=request.user.id))
        if org is not None:
            return True

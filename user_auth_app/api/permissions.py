from rest_framework.permissions import BasePermission

class IsMemberOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        is_owner = bool(request.user.id == obj.owner_id)
        is_member = obj.members.filter(id=request.user.id).exists()
        return is_owner or is_member
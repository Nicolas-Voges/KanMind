from rest_framework.permissions import BasePermission
from kanban_app.models import Board

class IsMemberOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):

        if request.method == 'DELETE':
            return bool(request.user and (request.user.id == obj.owner_id or request.user.is_superuser))
        else:
            is_owner = bool(request.user.id == obj.owner_id)
            is_member = obj.members.filter(id=request.user.id).exists()
            return is_owner or is_member
        

class IsMember(BasePermission):
    def has_permission(self, request, view):
        # return True
        # if request.method == 'POST':
        #     return bool(request.user.id and request.user.id in obj.board.members.all())
        # else:
        #     return False

        if request.method != 'POST':
            return False

        board_id = request.data.get('board')
        if not board_id:
            return False

        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            return False

        return request.user in board.members.all()
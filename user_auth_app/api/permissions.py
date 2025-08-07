from django.contrib.auth.models import User
from rest_framework.permissions import BasePermission
from kanban_app.models import Board, Task

class IsBoardMemberOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):

        if request.method == 'DELETE':
            return bool(request.user and (request.user == obj.owner or request.user.is_superuser))
        else:
            is_owner = bool(request.user.id == obj.owner_id)
            is_member = obj.members.filter(id=request.user.id).exists()
            return is_owner or is_member
        

class IsTaskBoardMember(BasePermission):
    def has_permission(self, request, view):
        board_id = request.data.get('board')
        if not board_id:
            return False

        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            return False

        return request.user in board.members.all()
    

class IsTaskBoardOwner(BasePermission):
    def has_permission(self, request, view):

        board_id = request.data.get('board')
        if not board_id:
            return False

        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            return False

        return request.user == board.owner
    

class IsTaskCreator(BasePermission):
    def has_object_permission(self, request, view, obj):
        creator_id = request.data.get('creator')
        if not creator_id:
            return False
        try:
            creator = User.objects.get(id=creator_id)
        except User.DoesNotExist:
            return False
        
        return request.user == creator
    

class IsTaskOwnerOrCreator(BasePermission):
    def has_object_permission(self, request, view, obj):
        board = obj.board
        creator = obj.creator
        return request.user in [board.owner, creator]

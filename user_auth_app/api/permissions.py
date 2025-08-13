from django.contrib.auth.models import User
from rest_framework.permissions import BasePermission
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import NotFound
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
    def has_object_permission(self, request, view, obj):
        board_id = request.data.get('board')
        if not board_id:
            raise NotFound("Board ID not provided.")

        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            raise NotFound("Board not found.")

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
    

class IsCommentBoardMember(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        task_id = view.kwargs['task_id']
        task = get_object_or_404(Task, pk=task_id)
        board = task.board
        return user.id in board.members.values_list('id', flat=True)
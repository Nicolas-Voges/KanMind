"""
Custom permission classes for the Kanban application.

These permissions restrict access to boards, tasks, and comments
based on user roles, board membership, and ownership.
"""


from django.contrib.auth.models import User
from rest_framework.permissions import BasePermission
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import NotFound
from kanban_app.models import Board, Task

class IsBoardMemberOrOwner(BasePermission):
    """
    Permission to check if the requesting user is a board member or owner.
    """


    def has_object_permission(self, request, view, obj):
        """
        Allow access if:
        - The request is DELETE and the user is the owner or a superuser.
        - For other methods, the user is either the board owner or a member.
        """
        if request.method == 'DELETE':
            return bool(request.user and (request.user == obj.owner or request.user.is_superuser))
        else:
            is_owner = bool(request.user.id == obj.owner_id)
            is_member = obj.members.filter(id=request.user.id).exists()
            return is_owner or is_member
        

class IsTaskBoardMember(BasePermission):
    """
    Permission to check if the requesting user is a member of the task's board.
    """


    def has_permission(self, request, view):
        """
        Allow access if the user is a member of the board associated with the task.
        Raise a NotFound error if the board does not exist.
        """
        if request.method != 'PATCH':
            board_id = request.data.get("board")
        else:
            task_id = view.kwargs.get('pk')
            try:
                board_id = Task.objects.get(id=task_id).board_id
            except:
                raise NotFound("Board not found.")

        if not board_id:
                raise NotFound("Board ID not provided.")


        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            raise NotFound("Board not found.")
        
        return board.members.filter(pk=request.user.pk).exists()
    

class IsTaskBoardOwner(BasePermission):
    """
    Permission to check if the requesting user is the owner of the task's board.
    """


    def has_permission(self, request, view):
        """
        Allow access if the user is the owner of the board specified in the request data.
        """
        board_id = request.data.get('board')
        if not board_id:
            return False

        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            return False

        return request.user == board.owner
    

class IsTaskCreator(BasePermission):
    """
    Permission to check if the requesting user is the creator of the task.
    """


    def has_object_permission(self, request, view, obj):
        """
        Allow access if the user is the creator specified in the request data.
        """
        creator_id = request.data.get('creator')
        if not creator_id:
            return False
        try:
            creator = User.objects.get(id=creator_id)
        except User.DoesNotExist:
            return False
        
        return request.user == creator
    

class IsTaskOwnerOrCreator(BasePermission):
    """
    Permission to check if the requesting user is the owner of the board
    or the creator of the task.
    """


    def has_object_permission(self, request, view, obj):
        """
        Allow access if the user is the board owner or the task creator.
        """
        board = obj.board
        creator = obj.creator
        return request.user in [board.owner, creator]
    

class IsCommentBoardMember(BasePermission):
    """
    Permission to check if the requesting user is a member of the board
    associated with the comment's task.
    """


    def has_permission(self, request, view):
        """
        Allow access if the user is a member of the board linked to the given task.
        Raise a 404 error if the task does not exist.
        """
        user = request.user
        task_id = view.kwargs['task_id']
        task = get_object_or_404(Task, pk=task_id)
        board = task.board
        return user.id in board.members.values_list('id', flat=True)
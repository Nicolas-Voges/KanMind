"""
API views for managing boards, tasks, and comments in the Kanban application.

This module contains Django REST Framework views for:
- Board CRUD operations
- Task creation, retrieval, update, and deletion
- Listing and creating comments for tasks
- Email-based user lookup

Permissions are enforced to restrict access based on user roles
and membership within boards.
"""


from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework import viewsets, status, generics, mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.exceptions import PermissionDenied
from user_auth_app.api.permissions import IsBoardMemberOrOwner, IsTaskBoardMember, \
    IsTaskOwnerOrCreator, IsCommentBoardMember
from kanban_app.models import Board, Task, Comment
from user_auth_app.api.serializers import UserAccountSerializer
from .serializers import BoardSerializer, BoardDetailSerializer, \
    TaskSerializer, CommentSerializer


class BoardViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing Board objects.

    Provides CRUD operations for boards. Access is restricted
    to authenticated users who are either members or the owner.
    """


    permission_classes = [IsAuthenticated, IsBoardMemberOrOwner]

    def perform_create(self, serializer):
        """
        Save a new Board instance with the requesting user as the owner.
        """
        serializer.save(owner=self.request.user)

    def get_serializer_class(self):
        """
        Return the appropriate serializer based on the action.
        """
        if self.action in ['retrieve', 'partial_update', 'update']:
            return BoardDetailSerializer
        return BoardSerializer

    def get_queryset(self):
        """
        Return a queryset of all boards.
        """
        return Board.objects.all().distinct()


class TaskCreateView(generics.CreateAPIView):
    """
    Create a new Task object.

    Only authenticated users who are members of the related board
    can create a task.
    """


    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsTaskBoardMember]

    def perform_create(self, serializer):
        """
        Save a new Task instance with the requesting user as the creator.
        """
        serializer.save(creator=self.request.user)


class TaskDetailUpdateDestroyView(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericAPIView
):
    """
    Retrieve, update, or delete a Task object.

    Permissions vary depending on the HTTP method:
    - DELETE: Requires the user to be the task owner or creator.
    - PATCH/PUT: Requires the user to be a member of the task's board.
    """


    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_permissions(self):
        """
        Return the appropriate permissions based on the request method.
        """
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsTaskOwnerOrCreator(),]
        return [IsAuthenticated(), IsTaskBoardMember()]

    def patch(self, request, *args, **kwargs):
        """
        Partially update the task.
        """
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        Delete the task.
        """
        return self.destroy(request, *args, **kwargs)


class TaskGetDetailView(APIView):
    """
    Retrieve tasks assigned to or to be reviewed by the requesting user.

    The endpoint behavior changes based on the request path:
    - If the path contains 'assigned-to-me', return assigned tasks.
    - Otherwise, return tasks where the user is the reviewer.
    """


    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Handle GET request to retrieve relevant tasks for the user.
        """
        if "assigned-to-me" in request.path:
            tasks = Task.objects.filter(
                assignee=request.user, board__members=request.user)
        else:
            tasks = Task.objects.filter(
                reviewer=request.user, board__members=request.user)
        serializer = TaskSerializer(
            tasks, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class CommentCreateListView(generics.ListCreateAPIView):
    """
    List or create comments for a specific task.

    Access is restricted to authenticated users who are members
    of the task's board.
    """


    permission_classes = [IsAuthenticated, IsCommentBoardMember]
    serializer_class = CommentSerializer

    def get_queryset(self):
        """
        Return all comments for the specified task.
        """
        task_id = self.kwargs['task_id']
        get_object_or_404(Task, pk=task_id)
        return Comment.objects.filter(task_id=task_id)

    def perform_create(self, serializer):
        """
        Save a new Comment instance with the requesting user as author.
        """
        task_id = self.kwargs['task_id']
        user_id = self.request.user.id
        serializer.save(
            author_id=user_id,
            task_id=task_id,
            created_at=timezone.now().date()
        )


class CommentDestroyView(generics.DestroyAPIView):
    """
    Delete a specific comment from a task.

    Access is restricted to authenticated users who are members
    of the task's board.
    """


    permission_classes = [IsAuthenticated, IsCommentBoardMember]
    lookup_field = 'id'
    lookup_url_kwarg = 'comment_id'

    def get_queryset(self):
        """
        Return the comment queryset filtered by task ID.
        """
        task_id = self.kwargs['task_id']
        return Comment.objects.filter(task_id=task_id)
    

class EmailCheckView(APIView):
    """
    Check if a user exists for the given email.

    Returns user data if found; otherwise, returns an error response.
    """


    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Handle GET request to check for a user by email.
        """
        email = request.query_params.get('email')
        if not email:
            return Response({"error": "Email parameter is required"}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Email not found"}, status=404)

        serializer = UserAccountSerializer(user)
        return Response(serializer.data, status=200)
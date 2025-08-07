from django.utils import timezone
from django.db.models import Q
from rest_framework import viewsets, status, generics, mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView
from user_auth_app.api.permissions import IsBoardMemberOrOwner, IsTaskBoardMember, \
    IsTaskOwnerOrCreator, IsCommentBoardMember
from kanban_app.models import Board, Task, Comment
from .serializers import BoardSerializer, BoardDetailSerializer, \
    TaskSerializer, CommentSerializer


class BoardViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsBoardMemberOrOwner]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_class(self):
        if self.action in ['retrieve', 'partial_update', 'update']:
            return BoardDetailSerializer
        return BoardSerializer

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct()


class TaskCreateView(generics.CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsTaskBoardMember]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class TaskDetailUpdateDestroyView(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericAPIView
):

    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsTaskOwnerOrCreator(),]
        return [IsAuthenticated(), IsTaskBoardMember()]

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class TaskGetDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
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
    permission_classes = [IsAuthenticated, IsCommentBoardMember]
    serializer_class = CommentSerializer

    def get_queryset(self):
        task_id = self.kwargs['task_id']
        return Comment.objects.filter(task_id=task_id)

    def perform_create(self, serializer):
        task_id = self.kwargs['task_id']
        user_id = self.request.user.id
        serializer.save(
            author_id=user_id,
            task_id=task_id,
            created_at=timezone.now().date()
        )


class CommentDestroyView(mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs['task_id']
        comment_id = self.kwargs['comment_id']
        return Comment.objects.filter()
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


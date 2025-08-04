from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from django.db.models import Q
from kanban_app.models import Board, Task
from .serializers import BoardSerializer, BoardDetailSerializer, \
TaskSerializer
from user_auth_app.api.permissions import IsMemberOrOwner, IsMember

class BoardViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsMemberOrOwner]
    
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
    permission_classes = [IsAuthenticated, IsMember]
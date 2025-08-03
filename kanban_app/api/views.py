from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from kanban_app.models import Board
from kanban_app.api.serializers import BoardSerializer, BoardDetailSerializer
from user_auth_app.api.permissions import IsMemberOrOwner

class BoardViewSet(viewsets.ModelViewSet):
    # queryset = Board.objects.all()
    # serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated, IsMemberOrOwner]

    def perform_create(self, serializer):
        serializer.save(owner_id=self.request.user)

    def get_serializer_class(self):
        if self.action in ['retrieve', 'partial_update', 'update']:
            return BoardDetailSerializer
        return BoardSerializer
    
    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(
            Q(owner_id=user.id) | Q(members=user)
        ).distinct()
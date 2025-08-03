from rest_framework import viewsets
from kanban_app.models import Board
from kanban_app.api.serializers import BoardSerializer, BoardDetailSerializer

class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    # serializer_class = BoardSerializer

    def perform_create(self, serializer):
        serializer.save(owner_id=self.request.user)

    def get_serializer_class(self):
        if self.action in ['retrieve', 'partial_update', 'update']:
            return BoardDetailSerializer
        return BoardSerializer
from rest_framework import viewsets
from kanban_app.models import Board
from kanban_app.api.serializers import BoardSerializer

class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

    def perform_create(self, serializer):
        serializer.save(owner_id=self.request.user)
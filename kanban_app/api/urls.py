from django.urls import path, include
from rest_framework import routers
from .views import BoardViewSet, TaskCreateView, TaskDetailUpdateDestroyView, TaskGetDetailView, \
CommentCreateListView, CommentDestroyView, EmailCheckView

router = routers.SimpleRouter()
router.register(r'boards', BoardViewSet, basename='board')

urlpatterns = [
    path('', include(router.urls)),
    path('tasks/', TaskCreateView.as_view(), name='task-post'),
    path('tasks/<int:pk>/', TaskDetailUpdateDestroyView.as_view(), name='task-detail'),
    path('tasks/assigned-to-me/', TaskGetDetailView.as_view(), name='assigned-to-me'),
    path('tasks/reviewing/', TaskGetDetailView.as_view(), name='review'),
    path('tasks/<int:task_id>/comments/', CommentCreateListView.as_view(), name='review'),
    path('tasks/<int:task_id>/comments/<int:comment_id>/', CommentDestroyView.as_view(), name='review'),
    path('email-check/', EmailCheckView.as_view(), name='email-check')
]
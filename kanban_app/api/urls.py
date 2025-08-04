from django.urls import path, include
from rest_framework import routers
from .views import BoardViewSet, TaskCreateView

router = routers.SimpleRouter()
router.register(r'boards', BoardViewSet, basename='board')

urlpatterns = [
    path('', include(router.urls)),
    path('tasks/', TaskCreateView.as_view(), name='task-post'),                               # POST
    # path('tasks/<int:pk>/', .as_view(), name='task-detail'),                          # PATCH DELETE
#     path('tasts/<int:pk>/comments/', .as_view(), name='review')                       # GET POST
#     path('tasts/<int:task_id>/comments/<int:comment_id>/', .as_view(), name='review') # DELETE
#     path('tasts/assigned-to-me/', .as_view(), name='assigned-to-me')                  # GET
#     path('tasts/reviewing/', .as_view(), name='review')                               # GET

#     path('email-check/', .as_view(), name='email-check')                              # GET
]
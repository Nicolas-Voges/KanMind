from django.urls import path, include
from rest_framework import routers
from .views import BoardViewSet

router = routers.SimpleRouter()
router.register(r'boards', BoardViewSet, basename='board')

urlpatterns = [
    path('', include(router.urls))
#     path('boards/', .as_view(), name='boards-list'),                                    POST GET
#     path('boards/<int:pk>/', .as_view(), name='board-detail'),                          GET PATCH DELETE

#     path('tasks/', .as_view(), name='task-list'),                                       POST
#     path('tasks/<int:pk>/', .as_view(), name='task-detail'),                            PATCH DELETE
#     path('tasts/<int:pk>/comments/', .as_view(), name='review')                         GET POST
#     path('tasts/<int:task_id>/comments/<int:comment_id>/', .as_view(), name='review')   DELETE
#     path('tasts/assigned-to-me/', .as_view(), name='assigned-to-me')                    GET
#     path('tasts/reviewing/', .as_view(), name='review')                                 GET

#     path('email-check/', .as_view(), name='email-check')                                GET
]
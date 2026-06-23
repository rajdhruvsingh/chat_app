from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .views import RegisterView, LoginView, WorkspaceViewSet, InviteMemberView, ChannelViewSet, MessageViewSet, RemoveMemberView, SearchUserView, NotificationViewSet, AttachmentUploadView, ActivityViewSet, ReactionView

router = DefaultRouter()
router.register('workspaces', WorkspaceViewSet, basename='workspace')
router.register('notification', NotificationViewSet, basename='notification')
router.register('activity', ActivityViewSet, basename='activity')

urlpatterns = [
    path('', include(router.urls)),
    path('attachments/upload/', AttachmentUploadView.as_view()),
    path('workspaces/<uuid:workspace_id>/members/<uuid:member_id>/remove/', RemoveMemberView.as_view()),
    path('search/', SearchUserView.as_view(), name='search'),
    path('workspaces/<uuid:workspace_id>/invite/', InviteMemberView.as_view()),
    path('workspaces/<uuid:workspace_id>/channels/', ChannelViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('workspaces/<uuid:workspace_id>/channels/<uuid:pk>/', ChannelViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    path('workspaces/<uuid:workspace_id>/channels/<uuid:channel_id>/messages/', MessageViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('workspaces/<uuid:workspace_id>/channels/<uuid:channel_id>/messages/<uuid:pk>/', MessageViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    path('message/<uuid:pk>/reactions/', ReactionView.as_view()),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
]
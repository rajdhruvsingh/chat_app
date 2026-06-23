from django.core.exceptions import ValidationError
from chat.serializers import AttachmentUploadSerializer
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django.db.models import Q
from chat.serializers import InviteMemberSerializer
from rest_framework.views import APIView
from rest_framework import viewsets
from .models import User, Workspace, WorkspaceMember, Channel, Message, Reaction, Notification, Attachment, Activity
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, WorkspaceSerializer, WorkspaceMemberSerializer, ChannelSerializer, MessageSerializer, ReactionSerializer, NotificationSerializer, AttachmentSerializer, ActivitySerializer, WorkspaceCreateSerializer, WorkspaceMemberSerializer, ChannelCreateSerializer, MessageCreateSerializer, ReactionSerializer, NotificationSerializer, AttachmentSerializer, ActivitySerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

# Create your views here.

class RegisterView(APIView):
    def post(self, request):
        serializer=RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user=serializer.save()
            return Response({"message":"User created successfully"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self,request):
        serializer=LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

class WorkspaceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Workspace.objects.filter(members__user=user)

    def get_serializer_class(self):
        if self.action == "create":
            return WorkspaceCreateSerializer
        return WorkspaceSerializer

    def create(self, request, *args, **kwargs):
        serializer = WorkspaceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workspace = serializer.save(owner=request.user)

        WorkspaceMember.objects.create(
            workspace=workspace,
            user=request.user,
            role=WorkspaceMember.Role.OWNER
        )
    
    def get_queryset(self):
        user = self.request.user
        return Workspace.objects.filter(members__user=user).order_by('-created_at')

        return Response(
            WorkspaceSerializer(workspace).data,
            status=status.HTTP_201_CREATED
        )

class InviteMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, workspace_id):
        workspace = Workspace.objects.filter(
            id=workspace_id
        ).first()

        if not workspace:
            return Response(
                {"message": "Workspace not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        is_authorised = WorkspaceMember.objects.filter(
            workspace=workspace,
            user=request.user,
            role__in=[
                WorkspaceMember.Role.OWNER,
                WorkspaceMember.Role.ADMIN
            ]
        ).exists()

        if not is_authorised:
            raise PermissionDenied("You are not authorised to invite members to this workspace")

        serializer = InviteMemberSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        user = data["user"]
        role = data["role"]

        if WorkspaceMember.objects.filter(
            workspace=workspace,
            user=user
        ).exists():
            return Response(
                {
                    "message": "User is already a member of this workspace"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        WorkspaceMember.objects.create(
            workspace=workspace,
            user=user,
            role=role
        )

        return Response(
            {"message": "Member invited successfully"},
            status=status.HTTP_200_OK
        )
            
class ChannelViewSet(viewsets.ModelViewSet):   
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        workspace_id = self.kwargs.get('workspace_id')
        workspace = Workspace.objects.filter(id=workspace_id).first()
        if not workspace:
            raise NotFound("Workspace not found")
        is_member=WorkspaceMember.objects.filter(
            workspace=workspace,
            user=self.request.user
        ).exists()
        if not is_member:
            raise PermissionDenied("You are not authorised to access this workspace")
        return Channel.objects.filter(workspace=workspace)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ChannelCreateSerializer
        return ChannelSerializer
    
    def perform_create(self, serializer):
        workspace_id = self.kwargs.get('workspace_id')
        workspace = Workspace.objects.filter(id=workspace_id).first()
        if not workspace:
            raise NotFound("Workspace not found")
        is_authorised=WorkspaceMember.objects.filter(
            workspace=workspace,
            user=self.request.user,
            role__in=[WorkspaceMember.Role.OWNER, WorkspaceMember.Role.ADMIN]
        ).exists()
        if not is_authorised:
            raise PermissionDenied("You are not authorised to create channels in this workspace")
        serializer.save(workspace=workspace)

class MessageViewSet(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['sender']
    search_fields = ['content']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        channel_id=self.kwargs.get('channel_id')
        channel = Channel.objects.filter(id=channel_id).first()
        if not channel:
            raise NotFound("Channel not found")
        is_member=WorkspaceMember.objects.filter(
            workspace=channel.workspace,
            user=self.request.user
        ).exists()
        if not is_member:
            raise PermissionDenied("You are not authorised to access this channel")
        return Message.objects.filter(channel=channel)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer
   
    def perform_create(self, serializer):
        channel_id = self.kwargs.get('channel_id')
        channel = Channel.objects.filter(id=channel_id).first()
        if not channel:
            raise NotFound("Channel not found")
        is_member=WorkspaceMember.objects.filter(
            workspace=channel.workspace,
            user=self.request.user
        ).exists()
        if not is_member:
            raise PermissionDenied("You are not authorised to access this channel")
        serializer.save(channel=channel,sender=self.request.user)

class RemoveMemberView(APIView):
    permission_classes=[IsAuthenticated]

    def delete(self, request, workspace_id, member_id):
        workspace = Workspace.objects.filter(id=workspace_id).first()
        if not workspace:
            return Response({"message":"Workspace not found"},status=status.HTTP_404_NOT_FOUND)
        is_authorised=WorkspaceMember.objects.filter(
            workspace=workspace,
            user=request.user,
            role__in=[WorkspaceMember.Role.OWNER, WorkspaceMember.Role.ADMIN]
        ).exists()
        if not is_authorised:
            return Response({"message":"You are not authorised to remove members from this workspace"},status=status.HTTP_401_UNAUTHORIZED)
        member = WorkspaceMember.objects.filter(
            workspace=workspace,
            user_id=member_id
        ).first()
        if not member:
            return Response({"message":"Member not found"},status=status.HTTP_404_NOT_FOUND)
        if member.role == WorkspaceMember.Role.OWNER:
            return Response({"message":"You cannot remove the owner from this workspace"},status=status.HTTP_400_BAD_REQUEST)
        member.delete()
        return Response({"message":"Member removed successfully"},status=status.HTTP_200_OK)

class SearchUserView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self, request):
        query=request.query_params.get('query', '')
        users=User.objects.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        ).exclude(id=request.user.id)[:50]
        serializer=UserSerializer(users, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
class NotificationViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    permission_classes=[IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    def retrieve(self, request, pk):
        notification = Notification.objects.filter(id=pk, user=request.user).first()
        if not notification:
            return Response({"message":"Notification not found"},status=status.HTTP_404_NOT_FOUND)
        notification.is_read = True
        notification.save()
        serializer=NotificationSerializer(notification)
        return Response(serializer.data,status=status.HTTP_200_OK)

class AttachmentUploadView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        user=request.user
        file=request.FILES.get('file')
        channel_id=request.data.get('channel_id')
        if not file or not channel_id:
            raise ValidationError("File and channel id are required")
        channel = Channel.objects.filter(id=channel_id).first()
        if not channel:
            raise NotFound("Channel not found")
        is_member=WorkspaceMember.objects.filter(
            workspace=channel.workspace,
            user=user
        ).exists()
        if not is_member:
            raise PermissionDenied("You are not authorised to upload files to this channel")
        message_id=request.data.get('message_id')
        message = None
        if message_id:
            message = Message.objects.filter(id=message_id).first()
            if not message:
                raise NotFound("Message not found")
        serializer=AttachmentUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        attachment=serializer.save(message=message, file_name=file.name)
        return Response(serializer.data,status=status.HTTP_200_OK)

class ActivityViewSet(ListModelMixin, GenericViewSet):
    permission_classes=[IsAuthenticated]
    serializer_class=ActivitySerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['action']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        return Activity.objects.filter(user=self.request.user).order_by('-timestamp')

class ReactionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        message = Message.objects.filter(id=pk).first()
        if not message:
            raise NotFound("Message Not Found")
        
        is_member = WorkspaceMember.objects.filter(
            workspace=message.channel.workspace,
            user=request.user
        ).exists()
        if not is_member:
            raise PermissionDenied("You are not authorised to react to this message")
        
        emoji = request.data.get('emoji')
        if not emoji:
            raise ValidationError("Emoji is required")
        
        reaction, created = Reaction.objects.get_or_create(
            message=message,
            user=request.user,
            emoji=emoji
        )
        if not created:
            reaction.delete()
            return Response({"message": "Reaction removed"}, status=status.HTTP_200_OK)
        
        serializer = ReactionSerializer(reaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
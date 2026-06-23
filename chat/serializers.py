from rest_framework import serializers
from chat.models import User, Workspace, WorkspaceMember, Channel, Message, Reaction, Notification, Attachment, Activity


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id', 'username', 'email', 'avatar', 'is_verified']

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password=serializers.CharField(write_only=True)
    class Meta:
        model=User
        fields=['username', 'email', 'password', 'confirm_password']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError("Email already exists")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user 

class LoginSerializer(serializers.Serializer):
    username=serializers.CharField()
    password=serializers.CharField(write_only=True)

    def validate(self, attrs):
        user=User.objects.filter(username=attrs['username']).first()
        if not user:
            raise serializers.ValidationError("User not found")
        if not user.check_password(attrs['password']):
            raise serializers.ValidationError("Invalid password")
        attrs['user'] = user 
        return attrs

class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','username', 'avatar', 'is_verified']

class WorkspaceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Workspace
        fields=['name']

class WorkspaceSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()

    class Meta:
        model=Workspace
        fields=['id', 'name', 'owner', 'member_count']

    def get_member_count(self, obj):
        return obj.member_count()

class WorkspaceMemberSerializer(serializers.ModelSerializer):
    user=UserPublicSerializer(read_only=True)
    role=serializers.CharField(required=False)
    class Meta:
        model=WorkspaceMember
        fields=['user', 'role']

class InviteMemberSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(
        choices=WorkspaceMember.Role.choices,
        required=False,
        default=WorkspaceMember.Role.MEMBER
    )

    def validate(self, attrs):
        email = attrs["email"]

        user = User.objects.filter(email=email).first()

        if not user:
            raise serializers.ValidationError(
                "User not found"
            )

        attrs["user"] = user

        return attrs

    def create(self, validated_data):
        return validated_data

class UserSearchSerializer(serializers.Serializer):
    query=serializers.CharField()
    workspace_id=serializers.UUIDField(required=False)

    def validate(self, attrs):
        workspace_id=attrs.get('workspace_id')
        user=attrs.get('user')
        if not workspace_id:
            return attrs
        workspace=Workspace.objects.filter(id=workspace_id).first()
        if not workspace:
            raise serializers.ValidationError("Workspace not found")
        return attrs

class ChannelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Channel
        fields=['name']

class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model=Channel
        fields=['id', 'name']

class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Message
        fields=['content']

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source='sender.username', read_only=True)
    class Meta:
        model=Message
        fields=['id', 'content', 'channel', 'sender', 'created_at', 'updated_at']

class MessageDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model=Message
        fields=['sender', 'attachments', 'reactions']

class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Reaction
        fields=['emoji']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model=Notification
        fields=['message','is_read']

class AttachmentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model=Attachment
        fields=['file']

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Attachment
        fields=['id','url','file_name']

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model=Activity
        fields=[ 'user', 'action', 'timestamp']   
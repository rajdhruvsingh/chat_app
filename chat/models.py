from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    avatar=models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_verified=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)

class Workspace(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name=models.CharField(max_length=100)
    owner=models.ForeignKey(User, on_delete=models.CASCADE, related_name='workspaces')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def member_count(self):
        return WorkspaceMember.objects.filter(workspace=self).count()

class WorkspaceMember(models.Model):
    workspace=models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='members')
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    class Role(models.TextChoices):
        OWNER = "OWNER"
        ADMIN = "ADMIN"
        MEMBER = "MEMBER"
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)

class Channel(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name=models.CharField(max_length=100)
    workspace=models.ForeignKey(Workspace, on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

class Message(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content=models.TextField()
    channel=models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='messages')
    sender=models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

class Reaction(models.Model):
    message=models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions')
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name='reactions')
    emoji=models.CharField(max_length=20)

class Notification(models.Model):
    message=models.ForeignKey(Message, on_delete=models.CASCADE, related_name='notifications')
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    is_read=models.BooleanField(default=False)

class Attachment(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message=models.ForeignKey(Message, on_delete=models.CASCADE, related_name='attachments')
    file=models.FileField(upload_to='attachments/')
    url=models.URLField(blank=True, null=True)
    file_name=models.CharField(max_length=100)
    uploaded_at=models.DateTimeField(auto_now_add=True)

class Activity(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action=models.CharField(max_length=100)
    resource_type=models.CharField(max_length=100)
    timestamp=models.DateTimeField(auto_now_add=True)
    
    
    
        

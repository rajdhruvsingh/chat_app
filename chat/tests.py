import _frozen_importlib_external
import _frozen_importlib_external
from datetime import timezone
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from chat.models import User, Workspace, WorkspaceMember

# Create your tests here.
class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # setup test data here
        self.user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword',
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_register_success(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'testpassword',
            'confirm_password': 'testpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_register_duplicate_email(self):
        response = self.client.post(reverse('register'), {
            'username': 'testuser2',
            'email': 'testuser@example.com',
            'password': 'testpassword',
            'confirm_password': 'testpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_login_wrong_password(self):
        response = self.client.post(reverse('login'), {'email': 'testuser@example.com', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class PermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # create users and workspace here

        self.owner = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='password'
        )

        self.member = User.objects.create_user(
            username='member',
            email='member@example.com',
            password='password'
        )
        self.non_member = User.objects.create_user(
            username='non_member',
            email='non_member@example.com',
            password='password'
        )

        self.workspace = Workspace.objects.create(
            name='Test Workspace',
            owner=self.owner
        )

        WorkspaceMember.objects.create(
            workspace=self.workspace,
            user=self.member,
            role=WorkspaceMember.Role.MEMBER
        )

        WorkspaceMember.objects.create(
            user=self.owner,
            workspace=self.workspace,
            role=WorkspaceMember.Role.OWNER
        )

    def test_unauthenticated_cannot_access_workspaces(self):
        response = self.client.get(reverse('workspace-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_member_cannot_access_workspace(self):
        self.client.force_authenticate(user=self.non_member)
        response = self.client.get(reverse('workspace-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_member_can_access_workspace(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.get(reverse('workspace-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_only_owner_can_invite(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.post(
            f'/api/workspaces/{self.workspace.id}/invite/',
            {'email': 'nonmember@example.com', 'role': 'MEMBER'}
        )
        print(response.data)  
        print(response.status_code)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
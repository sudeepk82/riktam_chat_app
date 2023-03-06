import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from chat_app.models import AppUser, Group
from utils import compare_dict


class Tests(APITestCase):
    def login_admin(self):
        """Login using 'test.admin@example.com' [SUPERUSER]"""
        admin = AppUser.objects.create_superuser(
            email="test.admin@example.com",
            password="Admin@123",
            first_name="Test",
            last_name="Admin",
        )
        self.client.force_login(user=admin)

    def test_create_user(self):
        """Validate Admin user creation"""
        self.login_admin()
        url = reverse("user-list")
        data = {
            "email": "test.user@example.com",
            "first_name": "Test",
            "last_name": "User",
            "is_superuser": False,
            "password": "User@123",
            "confirm_password": "User@123",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        dict_comp_res, diff_keys = compare_dict(
            data, response.data, ["confirm_password"]
        )
        self.assertTrue(
            dict_comp_res,
            f"Request Response dict comparison failed. Failed keys: {diff_keys}",
        )

    def test_negative_create_user(self):
        self.test_create_user()
        user = AppUser.objects.get(email="test.user@example.com")
        self.client.force_login(user=user)
        url = reverse("user-list")
        data = {
            "email": "test.user2@example.com",
            "first_name": "Test",
            "last_name": "User2",
            "is_superuser": False,
            "password": "User2@123",
            "confirm_password": "User2@123",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_account(self):
        """
        Check listing API works for users
        """
        url = reverse("user-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.test_create_user()
        response = self.client.get(url, format="json")
        self.assertEqual(
            len(response.data), 2
        )  # checking length 2 as we create an admin as well to create a user

    def test_negative_create_group(self):
        url = reverse("group-list")
        data = {
            "name": "Test group",
            "admin": 1,
            "description": "test group description",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_group(self):
        url = reverse("group-list")
        self.test_create_user()
        user = AppUser.objects.get(email="test.user@example.com")
        self.client.force_login(user=user)
        data = {
            "name": "Test group",
            "admin": user.id,
            "description": "test group description",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_user_to_group(self):
        self.test_create_group()
        group = Group.objects.all()[0]
        user = AppUser.objects.get(email="test.admin@example.com")
        data = {"userId": user.id}
        response = self.client.post(
            f"/groups/{group.id}/add_user/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(f"/groups/{group.id}/members/")
        self.assertIn(user.id, [member["id"] for member in response.data["data"]])

    def test_send_message(self):
        self.test_create_group()
        group = Group.objects.all()[0]
        user = AppUser.objects.get(email="test.admin@example.com")
        data = {
            "msg_text": "Test Message",
            "sender": user.id,
            "group": group.id,
            "like_users": [],
        }
        url = reverse("message-list")
        msg = self.client.post(url, data, format="json")
        response = self.client.get(f"/groups/{group.id}/messages/")
        comp_dict_res, diff_keys = compare_dict(msg.data, response.data["data"][0])
        self.assertTrue(
            comp_dict_res,
            f"Message body dict comparison failed. Failed keys: {diff_keys}",
        )

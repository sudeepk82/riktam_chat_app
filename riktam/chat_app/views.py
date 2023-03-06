from functools import partial
from bson import is_valid
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from chat_app.models import AppUser, Group, Message
from chat_app.serializers import AppUserSerializer, GroupSerializer, MessageSerializer
from rest_framework import viewsets, mixins, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (
    BasePermission,
    IsAuthenticated,
    IsAdminUser,
    SAFE_METHODS,
)
from rest_framework.authentication import BasicAuthentication
from utils import CsrfExemptSessionAuthentication
import json

# Create your views here.
# db = get_mongo_db()


def index(request):
    return HttpResponse("Chat App index working.")


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all().prefetch_related("appuser_set")
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated | ReadOnly]
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def create(self, request, *args, **kwargs):
        grp_inst = super(GroupViewSet, self).create(request, *args, **kwargs)
        grp_ser = self.add_user_to_group(request.data["admin"], grp_inst.data["id"])
        return Response({"data": grp_ser.data}, status=201)

    @action(methods=["post"], detail=True, url_path="add_user")
    def add_user(self, request, pk):
        user_id = request.data["userId"]
        grp_ser = self.add_user_to_group(user_id, pk)
        return Response({"data": grp_ser.data})

    @action(methods=["get"], detail=True, url_path="messages")
    def get_messages(self, request, pk):
        msgs = Message.objects.filter(group_id=pk)
        msg_ser = MessageSerializer(msgs, many=True)
        return Response({"data": msg_ser.data})

    @action(methods=["get"], detail=True, url_path="members")
    def get_members(self, request, pk):
        grp_obj = Group.objects.get(pk=pk)
        msg_ser = GroupSerializer(grp_obj)
        return Response({"data": msg_ser.data["members"]})

    def add_user_to_group(self, user_id, group_id):
        user = AppUser.objects.get(pk=user_id)
        group = Group.objects.get(pk=group_id)
        user.chat_groups.add(group)
        return GroupSerializer(group)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    @action(methods=["post"], detail=True, url_path="like")
    def like(self, request, pk):
        user_id = request.data["userId"]
        msg_obj = Message.objects.get(pk=pk)
        msg_dict = MessageSerializer(msg_obj).data
        if user_id in msg_dict["like_users"]:
            msg_dict["like_users"].remove(user_id)
        else:
            msg_dict["like_users"].append(user_id)
        msg_serializer = MessageSerializer(msg_obj, msg_dict)
        if msg_serializer.is_valid(raise_exception=True):
            msg_serializer.save()
            return Response({"data": msg_serializer.data})
        return HttpResponse({"message": "Like message operation failed"}, status=500)


class AppUserViewSet(viewsets.ModelViewSet):
    queryset = AppUser.objects.all().prefetch_related("created_groups")
    serializer_class = AppUserSerializer
    permission_classes = [IsAdminUser | ReadOnly]
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def get_permissions(self):
        if self.action in ["login"]:
            return []
        else:
            return [permission() for permission in self.permission_classes]

    @action(methods=["post"], detail=False, url_path="login")
    def login(self, request):
        username = request.data["username"]
        password = request.data["password"]
        print(username, password)
        user = authenticate(username=username, password=password)
        if user is not None:
            print("Authenticated...")
            login(request, user)
            return Response({"data": AppUserSerializer(user).data}, status=200)
        return Response({"message": "Invalid username or password."}, status=401)

    @action(methods=["get"], detail=True, url_path="logout")
    def logout(self, request, pk):
        logout(request)
        return Response({"message": "Logged out"}, status=200)

    @action(methods=["post"], detail=False, url_path="test")
    def test(self, request):
        print(request.data)


# from django.contrib.auth.views import LoginView
# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import csrf_exempt
# from django.http import HttpResponseRedirect


# class DangerousLoginView(LoginView):
#     """A LoginView with no CSRF protection."""

#     @method_decorator(csrf_exempt)
#     def dispatch(self, request, *args, **kwargs):
#         self.redirect_authenticated_user = False
#         return super(LoginView, self).dispatch(request, *args, **kwargs)

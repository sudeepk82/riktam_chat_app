# app/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.auth import login
from django.contrib.auth import get_user_model
from chat_app.models import Group, AppUser, Message
from chat_app.serializers import GroupSerializer, AppUserSerializer, MessageSerializer


class GroupConsumer(WebsocketConsumer):
    def connect(self):
        # self.room_group_name = "chat_app_connections"
        self.room_name = "chat_app_channel"
        async_to_sync(self.channel_layer.group_add)(self.room_name, self.channel_name)
        self.accept()
        print(self.channel_name)
        print(self.channel_layer.groups)
        print("Got group channels connection.")

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_name, self.channel_name
        )

    def receive(self, text_data):
        event_dict = json.loads(text_data)
        # user = get_user_model().objects.get(pk=event_dict["data"]["currentUser"])
        # async_to_sync(login)(self.scope, user)
        # self.scope["session"].save()
        event_name = event_dict["event_name"]
        self.__getattribute__(event_name)(event_dict)
        # async_to_sync(self.channel_layer.group_send)(
        #     self.room_name,
        #     {
        #         "type": event_name,
        #         "data": event_dict["data"],
        #     },
        # )

    def create_group(self, event_obj):
        group_req = event_obj["data"]
        group_ser = GroupSerializer(data=group_req)
        if group_ser.is_valid():
            group_ser.save()
            group_ser = self.add_user_to_group(group_req["admin"], group_ser.data["id"])
            async_to_sync(self.channel_layer.group_send)(
                self.room_name,
                {
                    "type": "group_created",
                    "data": group_ser.data,
                },
            )
        else:
            self.send(
                text_data=json.dumps(
                    {
                        "event_name": "error_alert",
                        "message": f"Failed to create group {group_req['name']}",
                    }
                )
            )

    def add_user(self, event_obj):
        user_req = event_obj["data"]
        group_ser = self.add_user_to_group(user_req["userId"], user_req["groupId"])
        async_to_sync(self.channel_layer.group_send)(
            self.room_name, {"type": "user_added", "data": group_ser.data}
        )

    def group_created(self, group_obj):
        print("group created", group_obj["data"])
        self.send(
            text_data=json.dumps({"event_name": "new_group", "data": group_obj["data"]})
        )

    def user_added(self, event_obj):
        self.send(
            text_data=json.dumps(
                {"event_name": "updated_group_members", "data": event_obj["data"]}
            )
        )

    def add_user_to_group(self, user_id, group_id):
        user = AppUser.objects.get(pk=user_id)
        group = Group.objects.get(pk=group_id)
        user.chat_groups.add(group)
        return GroupSerializer(group)


class ChatRoomConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = "chat_app_groups"
        self.room_name = self.scope["url_route"]["kwargs"]["group_id"]
        async_to_sync(self.channel_layer.group_add)(self.room_name, self.channel_name)
        self.accept()
        print(self.channel_layer.groups)
        print("Got Chat Room channels connection.")

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_name, self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        event_dict = json.loads(text_data)
        # user = get_user_model().objects.get(pk=event_dict["data"]["sender"])
        # async_to_sync(login)(self.scope, user)
        # self.scope["session"].save()
        event_name = event_dict["event_name"]
        self.__getattribute__(event_name)(event_dict["data"])
        # async_to_sync(self.channel_layer.group_send)(
        #     self.room_name,
        #     {
        #         "type": event_name,
        #         "data": event_dict["data"],
        #     },
        # )

    def like_message(self, event_obj):
        like_req = event_obj
        print("Liking")
        print(like_req)
        msg_obj = Message.objects.get(id=like_req["msgId"])
        msg_dict = MessageSerializer(msg_obj).data
        if (uid := like_req["userId"]) in msg_dict["like_users"]:
            print(uid)
            msg_dict["like_users"].remove(uid)
        else:
            print(uid)
            msg_dict["like_users"].append(uid)
        msg_serializer = MessageSerializer(msg_obj, msg_dict)
        if msg_serializer.is_valid(raise_exception=True):
            msg_serializer.save()
            async_to_sync(self.channel_layer.group_send)(
                self.room_name,
                {
                    "type": "message_liked",
                    "data": msg_serializer.data,
                },
            )

    def message_liked(self, msg_obj):
        self.send(
            text_data=json.dumps(
                {"event_name": "message_liked", "data": msg_obj["data"]}
            )
        )

    def send_message(self, event_obj):
        msg_req = event_obj
        print("sending message")
        print(msg_req)
        print(self.room_name)
        if int(self.room_name) == msg_req["group"]:
            msg_ser = MessageSerializer(data=msg_req)
            if msg_ser.is_valid():
                msg_ser.save()
                async_to_sync(self.channel_layer.group_send)(
                    self.room_name,
                    {
                        "type": "message_received",
                        "data": msg_ser.data,
                    },
                )
            else:
                print("INVALID REQUEST")
                self.send(
                    text_data=json.dumps(
                        {"event_name": "error_alert", "message": "SERVER ERROR!!!"}
                    )
                )
        else:
            self.send(
                text_data=json.dumps(
                    {"event_name": "error_alert", "message": "SERVER ERROR!!!"}
                )
            )

    def message_received(self, msg_obj):
        self.send(
            text_data=json.dumps(
                {"event_name": "message_received", "data": msg_obj["data"]}
            )
        )

from rest_framework import serializers
from chat_app.models import AppUser, Group, Message


class GroupSerializer(serializers.ModelSerializer):
    admin = serializers.PrimaryKeyRelatedField(queryset=AppUser.objects.all())
    members = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = "__all__"

    def get_members(self, obj):
        return list(map(lambda x: {"name": str(x), "id": x.id}, obj.appuser_set.all()))


class MessageSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(read_only=False)
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

    class Meta:
        model = Message
        fields = "__all__"

    def validate(self, data):
        sender_user = data["sender"]
        if data["group"] in list(sender_user.chat_groups.all()):
            return data
        else:
            raise serializers.ValidationError("sender not a member")

    def get_author(self, obj):
        return {"name": str(obj.sender), "id": obj.sender.id}


class AppUserSerializer(serializers.ModelSerializer):
    created_groups = serializers.SerializerMethodField()

    class Meta:
        model = AppUser
        fields = "__all__"

    def get_created_groups(self, obj):
        return list(map(str, obj.created_groups.all()))

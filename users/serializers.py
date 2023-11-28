# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from rest_framework import serializers
# from utils.upload import get_presigned_url

from .models import UserNotification
from video_library.settings import BASIC_IMAGE_URL


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.CharField()
    first_name = serializers.CharField(max_length=200)
    last_name = serializers.CharField(max_length=200)
    phone_number = serializers.CharField(max_length=200)
    password = serializers.CharField()
    class Meta:
        model = get_user_model()
        fields = (
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "password",
        )


class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=200)
    email = serializers.CharField(max_length=200)

    class Meta:
        model = get_user_model()
        fields = ("password", "email")


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField(max_length=200)
    last_name = serializers.CharField(max_length=200)
    phone_number = serializers.CharField(max_length=200)
    image_name = serializers.CharField(max_length=300)
    image_url = serializers.SerializerMethodField("_image_url")

    def _image_url(self, obj):
        if obj.image_url:
            if str(obj.image_url).startswith("user_images/"):
                return BASIC_IMAGE_URL + str(obj.image_url)
            elif obj.image_name:
                return get_presigned_url(obj.image_name)
            else:
                return str(obj.image_url)
        else:
            return None

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "image_name",
            "image_url",
        )


class ResetPasswordSerializer(serializers.Serializer):

    password = serializers.CharField(max_length=200)
    token = serializers.CharField(max_length=1000)



class UserNotesSerializer(serializers.Serializer):
    note_text = serializers.CharField()
    id = serializers.IntegerField()
    is_edited = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class UserNotificationsSerializer(serializers.Serializer):
    notification_text = serializers.CharField()
    created_at = serializers.DateTimeField()
    id = serializers.IntegerField()
    is_read = serializers.BooleanField()
    search_date = serializers.CharField(max_length=100)


class NotificationsSerializer(serializers.ModelSerializer):
    # created_at = serializers.DateTimeField(format = "%Y-%m-%d %H:%M:%S")

    class Meta:
        model = UserNotification
        fields = "__all__"


class EmptySerializer(serializers.Serializer):
    pass


class SharedNoteSerializer(serializers.Serializer):
    note_text = serializers.CharField()
    shared_by = serializers.CharField()
    id = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

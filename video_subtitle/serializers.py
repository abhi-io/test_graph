# -*- coding: utf-8 -*-
from datetime import datetime

from django.contrib.auth import get_user_model
from rest_framework import serializers
# from utils.upload import get_presigned_url

from .models import GraphQuery, NewsArticle
from video_library.settings import MEDIA_URL


class GraphQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = GraphQuery
        fields = "__all__"
        read_only_fields = ("created_at",)
class NewsArticleSerializer(serializers.ModelSerializer):
    published_date = serializers.DateField()
    class Meta:
        model = NewsArticle
        fields = "__all__"
        read_only_fields = ("created_at",)
class NewsArticleDateTimeSerializer(serializers.ModelSerializer): 
    published_date = serializers.DateField()
    count = serializers.IntegerField()

    class Meta:
        model = NewsArticle
        fields = ['published_date','count', 'id'] 

# class VideoSerializer(serializers.ModelSerializer):
    
#     class Meta:
#         model = Video
#         fields = (
#             "video_number",
#             "video_url",
#             "video_name",
#             "video_year",
#             "video_session",
#             "video_date",
#             "video_event",
#             "video_description",
#             "video_members",
#             "video_minister",
#             "video_sequence_number",
#             "video_tags",
#             "thumbnail", 
#         )


# class AdminVideoDetailsEditorSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Video
#         fields = (
#             "video_number",
#             "video_url",
#             "video_name",
#             "video_year",
#             "video_session",
#             "video_date",
#             "video_event",
#             "video_description",
#             "video_members",
#             "video_minister",
#             "video_sequence_number",
#             "video_tags",
#             "is_deleted",
#         )


# class VideoDetailSerializer(serializers.ModelSerializer):
#     video_tags = serializers.SerializerMethodField()
#     thumbnail = serializers.SerializerMethodField()

    
#     class Meta:
#         model = Video
#         fields = "__all__"

#     def get_video_tags(self, obj):
#         if obj.video_tags:
#             return obj.video_tags.split(",")
#         return []
    
#     def get_thumbnail(self, obj):
#         if obj.thumbnail:
#             return obj.thumbnail.url
#         return f"{MEDIA_URL}thumbnails/thumbnail.png"
    
    

# class SubTitleSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = VideoSubTitle
#         fields = (
#             "srt_sequence_number",
#             "video_id",
#             "start_time",
#             "end_time",
#             "sub_title",
#             "language_id",
#         )


# class SubTitleSerializerInput(serializers.ModelSerializer):
#     class Meta:
#         model = VideoSubTitle
#         fields = (
#             "srt_sequence_number",
#             "video_id",
#             "start_time",
#             "end_time",
#             "sub_title",
#             "language_id",
#             "uploded_user_id",
#         )


# class SubTitleSerializerEdit(serializers.ModelSerializer):
#     class Meta:
#         model = VideoSubTitle
#         fields = (
#             "srt_sequence_number",
#             "video_id",
#             "start_time",
#             "end_time",
#             "sub_title",
#             "language_id",
#             "uploded_user_id",
#             "is_deleted",
#         )


# class SubTitleSerializerList(serializers.ModelSerializer):
#     start_time = serializers.SerializerMethodField()
#     end_time = serializers.SerializerMethodField()
#     language_code = serializers.SerializerMethodField()
#     class Meta:
#         model = VideoSubTitle
#         fields = (
#             "id",
#             "video_id",
#             "srt_sequence_number",
#             "start_time",
#             "end_time",
#             "sub_title",
#             "uploded_user_id",
#             "updated_at",
#             "language_code",
#         )

#     def get_language_code(self, obj):
#         if obj.language:
#             return obj.language.language_code
#         return None

#     def get_start_time(self, obj):
#         if obj.start_time:
#             s = str(obj.start_time)
#             try:
#                 date_obj = datetime.strptime(s, '%H:%M:%S.%f')
#                 date_obj = datetime.strftime(date_obj, '%H:%M:%S.%f')
#                 time_var, millisec = date_obj.split(".")
#                 millisec = str(millisec).zfill(3)
#                 return time_var+"."+str(millisec[:3])
#             except:
#                 return s + ".000"
#         return None

#     def get_end_time(self, obj):
#         if obj.end_time:
#             s = str(obj.end_time)
#             try:
#                 date_obj = datetime.strptime(s, '%H:%M:%S.%f')
#                 date_obj = datetime.strftime(date_obj, '%H:%M:%S.%f')
#                 time_var, millisec = date_obj.split(".")
#                 millisec = str(millisec).zfill(3)
#                 return time_var+"."+str(millisec[:3])
#             except:
#                 return s + ".000"
#         return None


# class SubTitleDetailSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = VideoSubTitle
#         exclude = ["created_at", "updated_at"]


# class VideoSubTitleSerializer(serializers.ModelSerializer):
#     sub_titles = serializers.SerializerMethodField()

#     class Meta:
#         model = Video
#         fields = ("id", "video_name", "video_url", "sub_titles",

#                   )

#     def get_sub_titles(self, obj):
#         titles = []
#         for title in obj.videosubtitle_set.all():
#             data = SubTitleDetailSerializer(title, many=False)
#             titles.append(data.data)

#         return titles


# class LanguageSerializerInput(serializers.ModelSerializer):
#     class Meta:
#         model = Language
#         exclude = ["language_id", "created_at", "updated_at"]


# class LanguageSerializerDelete(serializers.ModelSerializer):
#     class Meta:
#         model = Language
#         exclude = ["created_at", "updated_at"]


# class LanguageSerializerList(serializers.ModelSerializer):
#     updatedat = serializers.DateTimeField(source='updated_at', format='%Y-%m-%d')

#     class Meta:
#         model = Language
#         fields = (
#             "language_id",
#             "language_code",
#             "language",
#             "updatedat",
#         )


# class HomeHighlightsSerializerList(serializers.ModelSerializer):
#     updatedat = serializers.DateTimeField(source='updated_at', format='%Y-%m-%d')
#     # video  = VideoSerializer(many=False)
#     video_data = serializers.SerializerMethodField()

#     def get_video_data(self, obj):
#         if obj.video_id:
#             return VideoSerializer(obj.video_id, many=False).data
#         return None
#     class Meta:
#         model = HomeHighlights
#         fields = (
#             "id",
#             "video_id",
#             "video_data",
#             "highlight_title",
#             "highlight_description",
#             "highlight_priority",
#             "uploded_user_id",
#             "updatedat",
#         )


# class HomeHighlightsSerializerInput(serializers.ModelSerializer):
#     class Meta:
#         model = HomeHighlights
#         fields = (
#             "video_id",
#             "highlight_title",
#             "highlight_description",
#             "highlight_priority",
#             "uploded_user_id",
#         )


# class HomeHighlightsSerializerEdit(serializers.ModelSerializer):
#     class Meta:
#         model = HomeHighlights
#         fields = (
#             "video_id",
#             "highlight_title",
#             "highlight_description",
#             "highlight_priority",
#             "uploded_user_id",
#         )

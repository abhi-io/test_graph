# -*- coding: utf-8 -*-
from itertools import groupby
from operator import itemgetter
from django.db import transaction
from rest_framework.authentication import SessionAuthentication

from authentication.authentication import JwtTokensAuthentication

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, F

from core_viewsets.custom_viewsets import FetchUpdateViewSets, ParameterSchema, ListCreateViewSet
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from utils.message_utils import get_message
from utils.pagination import CustomPageNumberPagination
# from .models import VideoSubTitle, Video, Language, HomeHighlights
from .models import  GraphQuery ,NewsArticle

from .serializers import (
    GraphQuerySerializer,
    NewsArticleSerializer,
    NewsArticleDateTimeSerializer,
#     SubTitleSerializerInput,
#     SubTitleSerializerEdit,

#     VideoSerializer,
#     VideoDetailSerializer,
#     VideoSubTitleSerializer,
#     AdminVideoDetailsEditorSerializer,

#     LanguageSerializerInput,
#     LanguageSerializerDelete,
#     LanguageSerializerList,

#     HomeHighlightsSerializerList,
#     HomeHighlightsSerializerInput,
#     HomeHighlightsSerializerEdit,
)
from video_library.settings import logger
from rest_framework.filters import BaseFilterBackend
import coreapi
from django.db.models import Q
import csv,json
from datetime import datetime
from .models import NewsArticle  # Replace 'myapp' with your actual app name
from django.core.management.base import BaseCommand
import pytz
import ast
from collections import OrderedDict
from django.http import JsonResponse

class VideoViewSet(viewsets.ModelViewSet):
    serializer_class = NewsArticleSerializer
    def list(self, request, *args, **kwargs):

        print("++++++++++++++++++++++")
        queryset = NewsArticle.objects.all()
        serializer = NewsArticleSerializer(queryset, many=True)
        print(serializer.data)
        return Response(
            {"code": 200, "message": get_message(200), "data": (serializer.data)},
            status=status.HTTP_200_OK,
        )
def fix_date(date_str):
    # Parse the original date-time string
    # The format is: 'MonthName day, year hours:minutes:seconds timezone'
    try:
        dt = datetime.strptime(date_str, '%B %d, %Y %H:%M:%S IST')

        # Convert to a timezone-aware datetime object
        # Assuming 'IST' stands for 'Indian Standard Time'
        ist = pytz.timezone('Asia/Kolkata')
        dt = ist.localize(dt)

        # Format the date-time to the new format: 'Year-month-day hours:minutes:seconds'
        formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:  
        formatted_date = None
    return formatted_date
         
class InserDataViewset(viewsets.ModelViewSet):
    serializer_class = NewsArticleSerializer

    def list(self, request, *args, **kwargs):
        with open('historic_articles.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                print(fix_date(row['published_at']))
                try:
                    with transaction.atomic():
                        NewsArticle.objects.create(
                            source=row['source'],
                            category=row['category'],
                            link=row['link'],
                            author=row['author'],
                            published_at = fix_date(row['published_at']),
                            # published_at=datetime.strptime(row['published_at'], '%Y-%m-%d %H:%M:%S'),  # Adjust date format as needed
                            header=row['header'],
                            subheader=row['subheader'],
                            content=row['content']
                        )
                     
                except Exception as e:
                    print(f"Error creating NewsArticle: {e}")
                    continue


        print("++++++++start++++++++++++++")
        queryset = NewsArticle.objects.all()
        serializer = NewsArticleSerializer(queryset, many=True)
        print(serializer.data)
        return Response(
            {"code": 200, "message": get_message(200), "data": (serializer.data)},
            status=status.HTTP_200_OK,
        )
class HandleQueryViewSet(viewsets.ModelViewSet):
    serializer_class = GraphQuerySerializer
    def list(self, request, *args, **kwargs):
        queryset = GraphQuery.objects.all()
        serializer = GraphQuerySerializer(queryset, many=True)
        list_of_tags = [field.name for field in NewsArticle._meta.get_fields()]
        my_tags_from_DB =  ['serch_text','date_range']
        list_of_tags = list_of_tags + my_tags_from_DB
        return Response(
            {"code": 200, "message": get_message(200), "data": list_of_tags},
            status=status.HTTP_200_OK,
        )
    def create(self, request, *args, **kwargs):
        print(request.data)  
        serializer = GraphQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"code": 200, "message": get_message(200), "data": (serializer.data)},
            status=status.HTTP_200_OK,
        ) 


class AnalyticsViewSet(viewsets.ModelViewSet):

    serializer_class = GraphQuerySerializer
    def list(self, request, *args, **kwargs):
        queryset = GraphQuery.objects.all()
        serializer = GraphQuerySerializer(queryset, many=True)

        def create_graph_data(query_id, dict_query_x, dict_query_y):
            # column = dict_query_x.key()
            dict_query_x = json.loads(dict_query_x)  
            dict_query_y = json.loads(dict_query_y)
            for key in dict_query_x.keys():
                print(key)
                dict_query_x_colomn = key
            for value in dict_query_x.values():
                print(value)
                dict_query_xvalue = value
            for key in dict_query_y.keys():
                print(key)
                dict_query_y_colomn = key
            for value in dict_query_y.values():
                print(value)
                dict_query_y_value = value
            if dict_query_y_colomn == 'date_range':
                filter_condition_x = {f'{"content"}__icontains': dict_query_xvalue}
                # filter_condition_y = {f'{dict_query_x_colomn}__icontains': dict_query_xvalue}
                dates = dict_query_y_value.split(",") 
                start_date = dates[0]
                end_date = dates[1] 
                #Q1
                queryset = NewsArticle.objects.filter(**filter_condition_x,published_at__range=(start_date, end_date))
                query_result = NewsArticleSerializer(queryset, many=True)
                               
                #Q2
                # queryset1 = (
                #         NewsArticle.objects.filter(**filter_condition_x)
                #         .values('published_at')
                #         .annotate(count=Count('id'), published_date=F('published_at__date') )
                #         .order_by('published_at')
                #     )
                
                # occurrences_data = NewsArticleDateTimeSerializer(queryset1, many=True).data
                
                di = {}
                for key,values in groupby(query_result.data, key=itemgetter('published_date')):
                    tmp ={}
                    d = list(values)
                    tmp['count'] = len(d)
                    tmp['data'] = d
                    di[key] =  tmp
                

                # return query_result, occurrences_data
                return di 

 
        db_data = serializer.data 
        for db_data_item in db_data:
            query_id = db_data_item.get("query_id", None)
            dict_query_x = db_data_item.get("dict_query_x", None)
            dict_query_y = db_data_item.get("dict_query_y", None)
            data  = create_graph_data(query_id, dict_query_x, dict_query_y) 
            # print(data , frequency)
             
        return Response(
            {"code": 200, "message": get_message(200), "data": data},
            status=status.HTTP_200_OK,
        )
         



    
    # pagination_class = CustomPageNumberPagination
    # serializer_class = VideoSerializer
    # authentication_classes = [JwtTokensAuthentication, SessionAuthentication]
    # queryset = Video.objects.all().order_by("-created_at")
    # schema = ParameterSchema(
    #     parameters={
    #         "list": [
    #             {
    #                 "name": "name",
    #                 "in": "query",
    #                 "required": False,
    #                 "description": "Quick search value",
    #                 "schema": {"type": "str", "default": ''},
    #             },
    #             {
    #                 "name": "tag",
    #                 "in": "query",
    #                 "required": False,
    #                 "description": "Quick search tag value",
    #                 "schema": {"type": "str", "default": ''},
    #             }
    #         ]
    #     }
    # )


    # def get_authenticators(self):
    #     print(self.request.__dict__)
    #     if self.request.method  == 'GET':
    #         return []
    #     return super().get_authenticators()

    # def list(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()
    #     search = request.query_params.get("search", None)
    #     tag = request.query_params.get("tag", None)
    #     do_include_deleted = request.query_params.get("do_include_deleted", False)

    #     queryset = queryset.filter(is_deleted=False)
    #     if do_include_deleted: 
    #         queryset = Video.objects.all()
    #     else:
    #         queryset = queryset.filter(is_deleted=False)
    #     if search:
    #         queryset = queryset.filter(video_name__icontains=search)
    #     if tag:
    #         queryset = queryset.filter(video_tags__icontains=tag)

    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = VideoDetailSerializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)

    #     serializer = VideoDetailSerializer(queryset, many=True)

    #     return Response(
    #         {"code": 200, "message": get_message(200), "data": serializer.data},
    #         status=status.HTTP_200_OK,
    #     )
    
    # def create(self, request, *args, **kwargs):

    #     self.video_uploaded_user_id = request.user.get("user_id")
    #     data = request.data
    #     #only if Admin
    #     user_id = request.user.get("user_id")
    #     check_if_Admin = get_user_model().objects.filter(id=user_id, is_superuser=True, is_active=True)
    #     if not check_if_Admin: 
    #         return Response(
    #             {"code": 403, "message": get_message(403_1)},
    #             status=status.HTTP_403_FORBIDDEN,
    #         )
    #     try:
    #         for single_video_data in data:
    #             tags = single_video_data.get("video_tags", [])
    #             tags = ','.join(tags)
    #             single_video_data["video_tags"] = tags
    #             serializer = VideoSerializer(data=single_video_data)
    #             if serializer.is_valid():
    #                 serializer.save()
    #             else:
    #                 return Response({"code": 400, "message": get_message(400), "error": serializer.errors, "error_field":single_video_data },
    #                     status=status.HTTP_400_BAD_REQUEST,)
    #         return Response({"code": 200, "message": get_message(200)},
    #                     status=status.HTTP_200_OK,)
    #     except Exception as e:
    #         logger.error("========================", str(e))
    #         return Response(
    #             {"code": 500, "message": get_message(500), "error": str(e)},
    #             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         )


    # def update(self, request, *args, **kwargs): 
    #     """
    #     to edit, hide, delete records
    #     """ 
    #     #only if Admin


    #     user_id = request.user.get("user_id")
    #     check_if_Admin = get_user_model().objects.filter(id=user_id, is_superuser=True, is_active=True)
    #     if not check_if_Admin: 
    #         return Response(
    #             {"code": 403, "message": get_message(403_1)},
    #             status=status.HTTP_403_FORBIDDEN,
    #         )
    #     video_id = kwargs["pk"]
    #     data = request.data
    #     tags = data.get("video_tags", [])
    #     if tags:
    #         tags = ','.join(tags)
    #         data["video_tags"] = tags
    #     try:
    #         video_obj = Video.objects.get(video_number=video_id)
    #     except ObjectDoesNotExist:
    #         return Response(
    #             {"code": 309, "message": get_message(309)},
    #             status=status.HTTP_400_BAD_REQUEST,
    #         )

    #     serializer = AdminVideoDetailsEditorSerializer(video_obj, data=data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(
    #             {"code": 200, "message": get_message(200)},
    #             status=status.HTTP_200_OK,
    #         )
    #     else:
    #         return Response(
    #             {"code": 400, "message": get_message(400), "error": serializer.errors},
    #             status=status.HTTP_400_BAD_REQUEST,
    #         ) 
        
####################################
####################################
####################################
####################################
####################################
####################################
####################################
####################################
####################################
# class SubTitleViewSet(ListCreateViewSet):
#     authentication_classes = [JwtTokensAuthentication, SessionAuthentication]
#     pagination_class = CustomPageNumberPagination
#     serializer_class = SubTitleSerializer
#     queryset = VideoSubTitle.objects.all()

#     schema = ParameterSchema(
#         parameters={
#             "list": [
#                 {
#                     "name": "search",
#                     "in": "query",
#                     "required": False,
#                     "description": "Quick search value",
#                     "schema": {"type": "str", "default": ''},
#                 },
#                 {
#                     "name": "language_key",
#                     "in": "query",
#                     "required": False,
#                     "description": "Language value",
#                     "schema": {"type": "str", "default": ''},
#                 },
#                 {
#                     "name": "video_id",
#                     "in": "query",
#                     "required": True,
#                     "description": "Video id",
#                     "schema": {"type": "str", "default": ''},
#                 }

#             ]
#         }
#     )


#     def get_authenticators(self):
#         if self.request.method  == 'GET':
#             return []
#         return super().get_authenticators()
    

#     def create(self, request, *args, **kwargs):
#         #create or update
#         """
#         {   "video_id": 2,
#             "language_code": "mal", 
#             "srt_data": [
#                     {
#                     "srt_sequence_number": 1,
#                     "start_time": "00:2:02",
#                     "end_time": "00:2:03",
#                     "sub_title": "ബിഹാറിന് പിന്നാലെ രാജസ്ഥാനിലുംതും",
#                 },
#                     {
#                     "srt_sequence_number": 2,
#                     "start_time": "00:3:02",
#                     "end_time": "00:4:03",
#                     "sub_title": "ബിഹാറിന്,,,,,,,,നിലുംതും",
#                 },
#                 ],
#         }
#         old:::::::::: {'srt_sequence_number': 21, 'video_id': 2, 'start_time': '00:2:02', 'end_time': '00:2:03', 'sub_title': ' ബിഹാറിന് പിന്നാലെ രാജസ്ഥാനിലും ജാതി സെൻസസ് നടത്തും ', 'language_code': 'en', 'language': <Language: English>}

#         """
#         #only if Admin/Editor 
#         user_id = request.user.get("user_id")
#         check_if_staff = get_user_model().objects.filter(id=user_id, is_staff=True, is_active=True)
#         if not check_if_staff: 
#             return Response( {"code": 403, "message": get_message(403_2)},   status=status.HTTP_403_FORBIDDEN,  )
         
#         data = request.data 
        
#         video = data.get("video_id")
#         language_code = data.get("language_code")
#         if not video:
#             return Response(
#                 {"code": 309, "message": get_message(309)},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#         try:
#             video_obj = Video.objects.get(video_number=video)
#         except ObjectDoesNotExist:
#             return Response(
#                 {"code": 309, "message": get_message(309)},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#         try:
#             lang_obj = Language.objects.get(language_code=itm.get("language_code"))
#         except ObjectDoesNotExist:
#             return Response(
#                 {"code": 707, "message": get_message(707)},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#         try:
#             with transaction.atomic():
#                 # delete older subtitles and recreate
#                 queryset = self.get_queryset().filter(video_id=video_obj, language=lang_obj)
#                 queryset.delete()
#                 for count, itm in enumerate(data['srt_data']):
#                     print(itm)
#                     itm["language"] = lang_obj
#                     serializer = SubTitleSerializerInput(data=itm)
#                     serializer.is_valid()
#                     obj = serializer.save()
#                     obj.video_id = video_obj
#                     obj.language = lang_obj
#                     # obj.srt_sequence_number = itm['srt_sequence_number']
#                     # obj.start_time = itm['start_time']
#                     # obj.end_time = itm['end_time']
#                     # obj.sub_title = itm['sub_title']
#                     obj.uploded_user_id = user_id
#                     try:
#                         obj.save()
#                     except Exception as e:
#                         print(e)
#                         return Response(
#                         {"code": 400, "message": get_message(400),
#                          "error": serializer.errors},
#                         status=status.HTTP_400_BAD_REQUEST,)

#                     # print(itm['sub_title'])
#             return Response(
#                     {"code": 200, "message": get_message(200)},
#                     status=status.HTTP_200_OK,
#                 )
#         except Exception as e:
#             return Response(
#                 {"code": 400, "message": get_message(400),
#                  "error": str(e)},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#     def list(self, request, *args, **kwargs):
#         """  can search with ?search=ravi,   ?video_id=2
#         """  
#         self.serializer_class=SubTitleSerializerList
#         queryset = self.get_queryset()
#         search_text = request.query_params.get("search", None)  #SEARCH 
#         language_key = request.query_params.get("language_key", None)  # language search key
#         target_video_id = request.query_params.get("video_id", None)
#         if target_video_id:
#             queryset = queryset.filter(video_id=target_video_id).filter(is_deleted=False)
#         if search_text:
#             queryset = queryset.filter(is_deleted=False).filter(
#                 Q(sub_title__icontains=search_text) | 
#                 Q(video_id__video_name__icontains=search_text) 
#                         )  #SEARCH query
#         if language_key:
#             queryset = queryset.filter(language__language_code__iexact=language_key)
#         page = self.paginate_queryset(queryset)
#         try:

#             if page is not None:
#                 serializer = SubTitleSerializerList(page, many=True)
#                 return self.get_paginated_response(serializer.data)
#             #normal user
#             serializer = SubTitleSerializerList(queryset, many=True)
#             return Response(
#                 {"code": 200, "message": get_message(200), "data": serializer.data},
#                 status=status.HTTP_200_OK,
#             )
#         except:
#             return Response(
#                 {"code": 715, "message": get_message(715)},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#     # def update(self, request, *args, **kwargs):
#     #     """
#     #     to edit, hide, delete records
#     #     """
#     #     self.authentication_classes = [JwtTokensAuthentication]
#     #     self.serializer_class = SubTitleSerializerEdit
#     #     #only if Admin/Editor
#     #     data = request.data
#     #     print("++++++++++++++")
#     #     user_id = request.user.get("user_id")
#     #     print("++++++++++++++")
#     #
#     #     language_code_1 = data.get("language_code", "en")
#     #     check_if_staff = get_user_model().objects.filter(id=user_id, is_staff=True, is_active=True)
#     #     if not check_if_staff:
#     #         return Response( {"code": 403, "message": get_message(403_2)},   status=status.HTTP_403_FORBIDDEN,  )
#     #
#     #     video_id = kwargs["pk"]
#     #     #check for language code
#     #     try:
#     #         lang_obj = Language.objects.get(language_code=language_code_1)
#     #         data["language"] = lang_obj
#     #     except ObjectDoesNotExist:
#     #         return Response(
#     #             {"code": 707, "message": get_message(707)},
#     #             status=status.HTTP_400_BAD_REQUEST,
#     #         )
#     #     #check for video
#     #     try:
#     #         video_obj = VideoSubTitle.objects.filter(video_id=video_id)
#     #     except ObjectDoesNotExist:
#     #         return Response(
#     #             {"code": 309, "message": "Video ID doesnot exist"},
#     #             status=status.HTTP_400_BAD_REQUEST,
#     #         )
#     #     try:
#     #         sub_titles =  data.get("srt_data", [])
#     #         print(len(sub_titles))
#     #         for itm in sub_titles:
#     #             print("---")
#     #             # Check if a record with the given video_id and language exists
#     #             video_obj = VideoSubTitle.objects.filter(
#     #                 video_id=video_id,
#     #                 id=itm['id'],
#     #                 ).first()
#     #             if video_obj:
#     #                 # Update the fields you want to edit
#     #                 video_obj.video = video_obj
#     #                 video_obj.language = lang_obj
#     #                 video_obj.srt_sequence_number = itm['srt_sequence_number']
#     #                 video_obj.start_time = itm['start_time']
#     #                 video_obj.end_time = itm['end_time']
#     #                 video_obj.sub_title = itm['sub_title']
#     #                 video_obj.uploded_user_id = user_id
#     #                 video_obj.save()
#     #             else:
#     #                 er_msg = "error while updating content at start time: " + itm['start_time'] + ", sub title: " + itm['sub_title'] + ",sequence is: " + str(itm['srt_sequence_number'])
#     #                 if video_obj is None:
#     #                     er_msg = "No record found for video_id: " + str(video_id) + ", subtitle id: " + str(itm['srt_sequence_number']) + ",start time: " + itm['start_time'] + ", sub title: " + itm['sub_title']
#     #                 return Response(
#     #                 {"code": 400, "message": er_msg},
#     #                 status=status.HTTP_400_BAD_REQUEST,)
#     #         return Response(
#     #                 {"code": 200, "message": get_message(200)},
#     #                 status=status.HTTP_200_OK,
#     #             )
#     #     except Exception as e:
#     #         return Response(
#     #             {"code": 400, "message": get_message(400), "error": e},
#     #             status=status.HTTP_400_BAD_REQUEST,
#     #         )


# class LanguageViewSet(viewsets.ModelViewSet):
#     # authentication_classes = [SessionAuthentication]
#     # pagination_class = CustomPageNumberPagination
#     serializer_class = LanguageSerializerInput
#     queryset = Language.objects.all()

#     def destroy(self, request, *args, **kwargs): 
#         self.authentication_classes = [JwtTokensAuthentication, SessionAuthentication]
#         data = request.data
#         serializer = LanguageSerializerDelete(data=data)
#         #only if Admin 
#         user_id = request.user.get("user_id") 
#         check_if_Admin = get_user_model().objects.filter(id=user_id, is_superuser=True, is_active=True)
#         if not check_if_Admin: 
#             return Response( {"code": 403, "message": get_message(403_1)},   status=status.HTTP_403_FORBIDDEN,  )
#         if serializer.is_valid():
#             Language.objects.filter(language_code=data['language_code']).delete()
#             return Response( {"code": 200, "message": get_message(200)},status=status.HTTP_200_OK,)
#         else:
#             return Response(
#                 {"code": 400, "message": get_message(400), "error": serializer.errors},status=status.HTTP_400_BAD_REQUEST,)

#     def create(self, request, *args, **kwargs): 
#         self.authentication_classes = [JwtTokensAuthentication, SessionAuthentication]
#         data = request.data
#         serializer = LanguageSerializerInput(data=data)
#         #only if Admin 
#         user_id = request.user.get("user_id") 
#         check_if_Admin = get_user_model().objects.filter(id=user_id, is_superuser=True, is_active=True)
#         if not check_if_Admin: 
#             return Response( {"code": 403, "message": get_message(403_1)},   status=status.HTTP_403_FORBIDDEN,  )
         
#         if serializer.is_valid(): 
#             Language.objects.update_or_create(language_code=data['language_code'], defaults=data)
#             return Response( {"code": 200, "message": get_message(200)},status=status.HTTP_200_OK,)
#         else:
#             return Response(
#                 {"code": 400, "message": get_message(400), "error": serializer.errors},status=status.HTTP_400_BAD_REQUEST,)

#     def list(self, request, *args, **kwargs):
#         """  can search with ?search=ravi
#         """
#         queryset = self.get_queryset()
#         serializer = LanguageSerializerList(queryset, many=True)
#         return Response(
#             {"code": 200, "message": get_message(200), "data": serializer.data},
#             status=status.HTTP_200_OK,
#         )
 

      
# class VideoHighlightsViewSet(viewsets.ModelViewSet):
 
#     serializer_class = HomeHighlightsSerializerInput
#     queryset = HomeHighlights.objects.all() 
#     authentication_classes = [JwtTokensAuthentication, SessionAuthentication]


#     def get_authenticators(self):
#         if self.request.method  == 'GET':
#             return []
#         return super().get_authenticators()

#     def create(self, request, *args, **kwargs):
#         data = request.data
#         serializer = HomeHighlightsSerializerInput(data=data)
#         #only if Admin 
#         user_id = request.user.get("user_id")
#         check_if_Admin = get_user_model().objects.filter(id=user_id, is_superuser=True, is_active=True)
#         if not check_if_Admin: 
#             return Response( {"code": 403, "message": get_message(403_1)},   status=status.HTTP_403_FORBIDDEN,  )
#         check_if_video_id_exits = Video.objects.filter(video_number=data['video_id'], is_deleted=False)
#         if not check_if_video_id_exits:
#             return Response( {"code": 309, "message": "invalid video ID"},status=status.HTTP_400_BAD_REQUEST,)
#         if serializer.is_valid():
#             obj = serializer.save()
#             obj.updated_by_user_id = user_id
#             obj.save()
#             return Response( {"code": 200, "message": get_message(200)},status=status.HTTP_200_OK,)
#         else:
#             return Response(
#                 {"code": 400, "message": get_message(400), "error": serializer.errors},status=status.HTTP_400_BAD_REQUEST,)

#     def list(self, request, *args, **kwargs):
#         """  No search
#         """
#         self.serializer_class = HomeHighlightsSerializerList
#         queryset = self.get_queryset().order_by('-highlight_priority')

#         #normal user
#         serializer = HomeHighlightsSerializerList(queryset, many=True)
#         # with VideoViewSet list video data with 'id'

#         print(serializer.data)
#         return Response(
#             {"code": 200, "message": get_message(200), "data": serializer.data},
#             status=status.HTTP_200_OK,
#         )
    
#     def update(self, request, *args, **kwargs):
#         """
#         to edit, hide, delete records
#         """

#         self.serializer_class = HomeHighlightsSerializerEdit
#         #only if Admin
#         user_id = request.user.get("user_id")
#         check_if_Admin = get_user_model().objects.filter(id=user_id, is_superuser=True, is_active=True)
#         if not check_if_Admin: 
#             return Response(
#                 {"code": 403, "message": get_message(403_1)},
#                 status=status.HTTP_403_FORBIDDEN,
#             )
#         c_id = kwargs["pk"]
#         data = request.data 
#         try:
#             member = HomeHighlights.objects.get(id=c_id)
#         except ObjectDoesNotExist:
#             return Response(
#                 {"code": 309, "message": "member not found"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#         serializer = HomeHighlightsSerializerEdit(member, data=data) 
#         if serializer.is_valid():   
#             obj = serializer.save()
#             obj.updated_by_user_id = user_id
#             obj.save()
#             return Response(
#                 {"code": 200, "message": get_message(200)},
#                 status=status.HTTP_200_OK,
#             )
#         else:
#             return Response(
#                 {"code": 400, "message": get_message(400), "error": serializer.errors},
#                 status=status.HTTP_400_BAD_REQUEST,
#             ) 
        
      
# class VideoTimelineViewSet(viewsets.ReadOnlyModelViewSet):
#     #normal user - no auth - GET only
#     serializer_class = VideoSerializer
#     queryset = Video.objects.all()

#     def list(self, request, *args, **kwargs):
#         """ On Video Page view, get all on the date and sort by video_sequence_number
#         """
        
#         self.serializer_class = VideoSerializer
#         try: 
#             video_id = int(request.query_params.get("video_id", None))
#             video_obj = Video.objects.get(video_number=video_id) 
#             queryset = self.get_queryset().filter(video_date=video_obj.video_date).order_by('video_sequence_number')
#             serializer = VideoSerializer(queryset, many=True)
#             return Response(
#                 {"code": 200, "message": get_message(200), "data": serializer.data},
#                 status=status.HTTP_200_OK,
#             )
#         except ObjectDoesNotExist:
#             return Response(
#                 {"code": 309, "message": "video not found on same date"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             ) 
 
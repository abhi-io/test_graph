# -*- coding: utf-8 -*-
"""djangobasics URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

# from .views import SubTitleViewSet, VideoViewSet,LanguageViewSet,VideoHighlightsViewSet,VideoTimelineViewSet
from .views import VideoViewSet , InserDataViewset, HandleQueryViewSet, AnalyticsViewSet

router = DefaultRouter(trailing_slash=False)

router.register(r"data", VideoViewSet, basename="video")
#COMMENTING FOR SAFTY router.register(r"insert", InserDataViewset, basename="language")
router.register(r"query", HandleQueryViewSet, basename="qq")
router.register(r"analytics", AnalyticsViewSet, basename="Analytics ")


urlpatterns = [
    path(r"", include(router.urls)),
]

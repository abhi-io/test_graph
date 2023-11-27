from django.urls import path
from .views import HiView

urlpatterns = [
    path('hi/', HiView.as_view(), name='hi'),
]
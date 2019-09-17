from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('subscribe/',views.subscribe, name='subscribe'),
    path('download/<str:filename>/',views.download, name='download'),
]

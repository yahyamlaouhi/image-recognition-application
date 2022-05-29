# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('accuracy/', views.accuracy, name='accuracy'),
    path('dashboard/accuracy/', views.accuracy, name='accuracy'),
    path('accuracy/dashboard/', views.dashboard, name='dashboard'),





    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]

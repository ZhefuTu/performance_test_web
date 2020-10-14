"""TestPlatform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
import views

urlpatterns = [
    url(r'^index', views.index),
    url(r'^empty', views.empty),
    url(r'^performance_test', views.show_performance_test),
    url(r'^perf_data', views.get_perf_data),
    url(r'^release_test', views.show_release_test),
    url(r'^show_report', views.show_report),
]

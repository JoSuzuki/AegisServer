from django.urls import path

from . import views

urlpatterns = [
  path('single_request_login', views.single_request_login, name='single_request_login'),
  path('test', views.test, name='test')
]
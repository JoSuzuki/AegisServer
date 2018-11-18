from django.urls import path

# from django.conf.urls import url, include
import pignus.views as views

urlpatterns = [
  path('single_request_login', views.single_request_login, name='single_request_login'),
  path('test', views.test, name='test'),
  path('users', views.users, name='users')
]

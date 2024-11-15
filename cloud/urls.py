# 编写urls.py文件，定义路由规则
from django.urls import path
from .views import file_list_view, delete_file_view, configure_s3_view, search

app_name = 'cloud'
urlpatterns = [
    path('files/', file_list_view, name='file_list'),
    path('delete_file/', delete_file_view, name='delete_file'),
    path('login_s3/', configure_s3_view, name='configure_s3'),
    path('search/', search, name='search'),
]
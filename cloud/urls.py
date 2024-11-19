# 编写urls.py文件，定义路由规则
from django.urls import path

from . import views
from .views import list_view, delete_file_view, configure_s3_view, search, user_login, user_logout

from .api_views import (
    api_get_s3_config,
    api_configure_s3,
    api_upload_files,
    api_list_files,
    api_search_files,
    api_delete_file
)

app_name = 'cloud'
urlpatterns = [
    path('index/', list_view, name='index'),  # 首页的 URL 路由
    path('login/', user_login, name='login'),  # 用户登录的 URL 路由
    path('logout/', user_logout, name='logout'),  # 用户登出
    path('delete_file/', delete_file_view, name='delete_file'),
    path('login_s3/', configure_s3_view, name='configure_s3'),
    path('search/', search, name='search'),

    # 新增的 API 接口
    path('api/s3/config/', api_get_s3_config, name='api_get_s3_config'),
    path('api/s3/configure/', api_configure_s3, name='api_configure_s3'),
    path('api/files/upload/', api_upload_files, name='api_upload_files'),
    path('api/files/', api_list_files, name='api_list_files'),
    path('api/files/search/', api_search_files, name='api_search_files'),
    path('api/files/delete/', api_delete_file, name='api_delete_file'),

]

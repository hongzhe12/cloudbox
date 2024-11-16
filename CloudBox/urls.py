"""
URL configuration for CloudBox project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.urls import re_path
from django.views.static import serve
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from cloud import views

# 创建 API 文档视图
schema_view = get_schema_view(
    openapi.Info(
        title="Cloud File Management API",  # API 文档的标题
        default_version='v1',  # API 的默认版本
        description="API documentation for cloud file management service",  # API 描述
        terms_of_service="https://www.google.com/policies/terms/",  # 服务条款链接（可选）
        contact=openapi.Contact(email="youremail@example.com"),  # 联系信息（可选）
        license=openapi.License(name="MIT License"),  # 许可证（可选）
    ),
    public=True,  # 公共访问权限，默认为 True，表示文档是公开的
    permission_classes=(permissions.AllowAny,),  # 设置谁可以访问该文档，这里表示任何人都可以访问
)

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('cloud/', include('cloud.urls')),
                  # 添加 API 文档的 URL 路由
                  path('swagger/', schema_view.with_ui('swagger', cache_timeout=0),
                       name='schema-swagger-ui'),  # Swagger UI

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += [
        re_path(
            r"^media/(?P<path>.*)$",
            serve,
            {
                "document_root": settings.MEDIA_ROOT,
            },
        ),
    ]

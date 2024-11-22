from django.contrib import admin
from .models import S3Config

class S3ConfigAdmin(admin.ModelAdmin):
    # 重写 get_queryset 方法，只返回当前用户的 S3Config
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:  # 如果是管理员，返回所有记录
            return queryset
        return queryset.filter(user=request.user)  # 否则只返回当前用户的记录

    # 禁止编辑 user 字段，确保用户无法修改此字段
    # readonly_fields = ['user']  # user 字段只读

    # 可选：定义哪些字段在列表页显示
    list_display = ['access_key', 'secret_key', 'bucket_name', 'end_point']

    # 如果想更精细控制表单字段，禁止编辑 user 字段
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:  # 如果是编辑已有记录，禁止修改 user 字段
            form.base_fields['user'].disabled = True
        return form

admin.site.register(S3Config, S3ConfigAdmin)

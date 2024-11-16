from django.db import models
from django.contrib.auth.models import User  # 引入 User 模型

class S3Config(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='s3_config')  # 每个用户只有一个配置
    access_key = models.CharField(max_length=255)
    secret_key = models.CharField(max_length=255)
    bucket_name = models.CharField(max_length=255)
    end_point = models.CharField(max_length=255)

    def __str__(self):
        return f"S3 Config ({self.bucket_name}) for {self.user.username}"

    class Meta:
        verbose_name = "S3 配置"  # 设置单数名称
        verbose_name_plural = "S3 配置"  # 设置复数名称

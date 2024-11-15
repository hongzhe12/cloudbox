from django.db import models


class S3Config(models.Model):
    access_key = models.CharField(max_length=255)
    secret_key = models.CharField(max_length=255)
    bucket_name = models.CharField(max_length=255)
    end_point = models.CharField(max_length=255)

    def __str__(self):
        return f"S3 Config ({self.bucket_name})"

    class Meta:
        verbose_name = "S3 配置"  # 设置单数名称
        verbose_name_plural = "S3 配置"  # 设置复数名称

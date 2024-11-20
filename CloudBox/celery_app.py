from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# 设置 Django 的 settings 模块路径
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CloudBox.settings')

app = Celery('CloudBox')

# 配置 Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现任务
app.autodiscover_tasks()

# 设置 worker_pool 为 solo 模式
# app.conf.worker_pool = 'solo' # 测试环境（只能处理一个任务）

app.conf.worker_pool = 'prefork' # 默认并发模式

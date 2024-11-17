from __future__ import absolute_import, unicode_literals

# 从 celery_app.py 导入 Celery 实例
from .celery_app import app as celery_app

__all__ = ('celery_app',)

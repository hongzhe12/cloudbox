#!/bin/sh

# 收集静态文件
python manage.py collectstatic --noinput

# 检测模型变化
python manage.py makemigrations

# 数据库迁移
python manage.py migrate

# 启动 Django 开发服务器
uvicorn CloudBox.asgi:application --host 0.0.0.0 --port 8000 --workers 10
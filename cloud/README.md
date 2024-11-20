# 测试步骤

### 测试redis连通

```bash
docker exec -it cloudbox-web bash
python manage.py shell
```

在 Django Shell 中：

```python
from django.core.cache import cache
cache.set('test_key', 'test_value', timeout=60)
print(cache.get('test_key'))  # 应该输出 'test_value'
```


### 创建管理员账户
```bash
docker compose exec -uroot web python manage.py createsuperuser
```


### 初始化模型
```bash
docker compose exec -uroot web python manage.py makemigrations cloud
docker compose exec -uroot web python manage.py migrate cloud
```

### 启动celery
```bash
celery -A CloudBox.celery_app worker --loglevel=info
celery -A CloudBox.celery_app worker --loglevel=info --concurrency=4
celery -A CloudBox.celery_app worker --loglevel=DEBUG
```


如果你的 Django 项目仍然沿用之前的缓存，清理缓存的步骤可以帮助确保所有缓存数据得到刷新，避免浏览器缓存和服务器端缓存造成的不一致问题。

### 1. **清理 Django 的缓存**

#### 清理内存缓存（如 Redis）

如果你使用的是 **Redis** 或类似的缓存系统，可以手动清除缓存。通常，Django 会使用 `django-redis` 或其他缓存后端，你可以通过以下方式清除缓存：

- **使用 Django shell 手动清除缓存**

你可以使用 Django 的 `shell` 命令进入 Django 的 Python 环境，并手动清除缓存。比如清除 `file_list` 缓存：

```bash
docker compose exec -uroot web python manage.py shell
```

进入 Django shell 后：

```python
from django.core.cache import cache
cache.clear()  # 清除所有缓存
# 或者清除特定的缓存
cache.delete('file_list')  # 删除特定缓存项
```



### 2. **清理数据库中的缓存**

有时候，Django 自带的 `django.contrib.sessions` 或其他模型级的缓存也可能会影响你对缓存的访问。你可以通过清除数据库中的缓存来解决问题。

#### 清除 Session 缓存

如果你使用的是数据库存储的会话（Session）缓存，你可以通过以下命令来清理它：

```bash
python manage.py clearsessions
```

这将清理所有过期的会话记录。

### 3. **清理 Celery 或其他任务队列的缓存**

如果你在项目中使用了 Celery 或其他任务队列来处理异步任务，确保任务队列中的缓存也被清理。你可以通过 Celery 的后台管理工具来清理任务队列，或者手动取消正在进行的任务。

#### 清理 Celery 中的任务队列

```bash
celery -A CloudBox control cancel_consumer
```
以确保浏览器和服务器端的缓存都得到清理，解决加载旧数据或静态文件缓存问题。


# 查看容器完整的command
```bash
docker inspect --format '{{json .Config.Cmd}}' cloudbox-celery
```
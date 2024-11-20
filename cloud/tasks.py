from celery import shared_task
from django.core.cache import cache

from .s3client import S3Client
from .utils import compress_image
from .conf import REDIS_TIMEOUT

'''
celery -A CloudBox.celery_app worker --loglevel=info
celery -A CloudBox.celery_app worker --loglevel=info --concurrency=4
celery -A CloudBox.celery_app worker --loglevel=DEBUG
'''



# @shared_task
# def upload_file_to_s3(file_name, file_content, access_key, secret_key, bucket_name, end_point):
#     lock_key = f'upload_file_lock_{file_name}'

#     # 获取缓存锁，超时3秒
#     with cache.lock(lock_key, timeout=3):
#         try:
#             s3_client = S3Client(access_key, secret_key, bucket_name, end_point)
#             compressed_file = compress_image(file_content)

#             # 上传文件到 S3
#             result = s3_client.put_file(file_name, compressed_file)

#             if result:
#                 # 更新缓存
#                 list_files = cache.get('file_list', [])
#                 new_file = s3_client.get_file_info_by_name(file_name)
#                 list_files.append(new_file)
#                 cache.set('file_list', list_files, timeout=REDIS_TIMEOUT)

#             return result
#         except Exception as e:
#             return {'success': False, 'error': str(e)}

from redis.exceptions import LockNotOwnedError
import logging

logger = logging.getLogger(__name__)

@shared_task
def upload_file_to_s3(file_name, file_content, access_key, secret_key, bucket_name, end_point):
    lock_key = f'upload_file_lock_{file_name}'
    lock_timeout = 60  # 锁超时时间（秒）

    # 获取缓存锁，设置超时时间
    lock = cache.lock(lock_key, timeout=lock_timeout)
    if not lock.acquire(blocking=False):  # 非阻塞模式尝试获取锁
        logger.warning(f"Task for {file_name} skipped because another task is processing it.")
        return {'success': False, 'error': f"File {file_name} is locked by another process."}

    try:
        s3_client = S3Client(access_key, secret_key, bucket_name, end_point)
        compressed_file = compress_image(file_content)

        # 上传文件到 S3
        result = s3_client.put_file(file_name, compressed_file)

        if result:
            # 更新缓存
            list_files = cache.get('file_list', [])
            new_file = s3_client.get_file_info_by_name(file_name)
            list_files.append(new_file)
            cache.set('file_list', list_files, timeout=REDIS_TIMEOUT)

        return result
    except Exception as e:
        logger.error(f"Error uploading file {file_name}: {str(e)}")
        return {'success': False, 'error': str(e)}
    finally:
        try:
            # 尝试释放锁
            lock.release()
        except LockNotOwnedError:
            logger.warning(f"Lock for {file_name} was already released or expired.")

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
#     s3_client = S3Client(access_key, secret_key, bucket_name, end_point)
#     compressed_file = compress_image(file_content)
#     result = s3_client.put_file(file_name, compressed_file)
#
#     if result:
#         # 更新缓存
#         list_files = cache.get('file_list', [])
#         new_file = s3_client.get_file_info_by_name(file_name)
#         list_files.append(new_file)
#         cache.set('file_list', list_files, timeout=REDIS_TIMEOUT)
#
#     return result


@shared_task
def upload_file_to_s3(file_name, file_content, access_key, secret_key, bucket_name, end_point):
    lock_key = f'upload_file_lock_{file_name}'

    # 获取缓存锁，超时3秒
    with cache.lock(lock_key, timeout=30):
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
            return {'success': False, 'error': str(e)}
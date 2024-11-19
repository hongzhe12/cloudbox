import hashlib
import functools

from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from .conf import REDIS_TIMEOUT


def catch_exceptions_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"An error occurred in {func.__name__}: {e}")
            # 你可以在这里进行其他的异常处理或记录日志
            return None  # 如果需要，也可以返回其他值或重新引发异常

    return wrapper


def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


import boto3
import os
from botocore.config import Config


class S3Client:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(S3Client, cls).__new__(cls)
        return cls._instance

    def __init__(self, access_key, secret_key, bucket_name, end_point=None, region='us-east-1'):
        if not hasattr(self, 'initialized'):  # 检查是否已经初始化
            self.access_key = access_key
            self.secret_key = secret_key
            self.end_point = end_point
            self.region = region
            self.bucket_name = bucket_name
            self.s3 = self.init_s3(access_key, secret_key, end_point, region)
            self.initialized = True  # 标记为已初始化

    @functools.lru_cache(None)  # 缓存 S3 客户端以避免重复创建
    def init_s3(self, access_key, secret_key, end_point, region):
        """
        初始化 S3 客户端
        :param access_key: AWS Access Key
        :param secret_key: AWS Secret Key
        :param end_point: Endpoint URL
        :param region: AWS region
        :return: S3 client
        """
        return boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            use_ssl=True,
            region_name=region,
            endpoint_url=end_point,
            config=Config(
                s3={"addressing_style": "path"},
                retries={'max_attempts': 10, 'mode': 'standard'},
                max_pool_connections=10  # 启用连接池
            )
        )

    def get_file(self, filename):
        s3 = self.s3
        bucket_name = self.bucket_name

        return s3.get_object(
            Bucket=bucket_name,
            Key=filename,
        )

    def get_file_info_by_name(self, file_name):
        """
        按文件名查找文件，并返回文件信息字典
        :param file_name: 文件名
        :return: 文件信息字典（包含 'name', 'size', 'last_modified', 'etag', 'url' 等字段）
        """
        try:
            # 列出桶内的文件
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=file_name)
            if 'Contents' not in response:
                return None  # 如果没有文件匹配，返回 None

            file_info = None
            for file in response['Contents']:
                if file['Key'] == file_name:
                    # 如果找到匹配的文件，获取详细信息
                    file_info = {
                        'name': file['Key'],
                        'size': file['Size'] // 1024,  # 转换为 KB
                        'last_modified': file['LastModified'].strftime('%Y-%m-%d %H:%M:%S'),  # 格式化时间
                        'etag': file['ETag'].strip('"'),  # 清除双引号
                        'url': self.s3.generate_presigned_url(
                            'get_object',
                            Params={'Bucket': self.bucket_name, 'Key': file['Key']},
                            ExpiresIn=REDIS_TIMEOUT  # 设置预签名 URL 过期时间（单位秒）
                        )
                    }
                    break  # 找到后可以退出循环

            return file_info

        except (NoCredentialsError, PartialCredentialsError) as e:
            print(f"S3 credentials error: {e}")
            return None
        except Exception as e:
            print(f"Error fetching file info: {e}")
            return None

    @catch_exceptions_decorator
    def put_file(self, filename, file):
        s3 = self.s3
        bucket_name = self.bucket_name

        try:
            # 将 InMemoryUploadedFile 对象的内容作为字节流上传到 S3
            return s3.put_object(
                Bucket=bucket_name,
                Body=file.read(),  # 读取文件内容
                Key=filename,
            )
        except Exception as e:
            print(f"上传文件 {filename} 失败: {str(e)}")
            return None

    def have_bucket(self):
        s3 = self.s3
        bucket_name = self.bucket_name

        buckets = s3.list_buckets()['Buckets']
        for bucket in buckets:
            if bucket_name == bucket['Name']:
                return True
        return False

    def download_file(self, filename, local_filename):
        """Download a file from S3 and save it locally."""
        s3 = self.s3
        bucket_name = self.bucket_name

        response = self.get_file(filename)
        with open(local_filename, 'wb') as f:
            f.write(response['Body'].read())
        print(f"File '{filename}' has been downloaded and saved as '{local_filename}'.")

    def list_files(self) -> list:
        """List all files in the specified S3 bucket."""
        print("获取文件列表...")
        s3 = self.s3
        bucket_name = self.bucket_name

        file_items = []
        response = s3.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in response:
            for obj in response['Contents']:
                file_key = obj['Key']
                file_size = obj['Size'] // 1024  # 转换为KB单位
                last_modified = obj['LastModified'].strftime("%Y-%m-%d %H:%M:%S")  # 格式化为字符串
                etag = obj['ETag'].strip('"')  # 去掉引号
                storage_class = obj['StorageClass']
                file_url = s3.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket_name, 'Key': file_key},
                    ExpiresIn=REDIS_TIMEOUT  # 预签名 URL 的有效期，单位为秒
                )
                file_items.append({
                    'name': file_key,  # 文件的完整路径名称（包括文件夹路径）
                    'size': file_size,  # 文件大小，单位为 KB
                    'last_modified': last_modified,  # 文件的最后修改时间，格式为字符串
                    'etag': etag,  # 文件的 ETag，通常是 MD5 校验值（未启用多部分上传时）
                    'storage_class': storage_class,  # 文件的存储类别（如 Standard、Glacier 等）
                    'url': file_url  # 文件的预签名 URL，可用于直接访问或下载文件
                })

        else:
            print("The bucket is empty or does not exist.")

        return file_items

    @catch_exceptions_decorator
    def upload_folder(self, folder_path):
        """Upload all files in a folder to the specified S3 bucket, preserving the folder structure."""
        bucket_name = self.bucket_name

        target_folder_name = os.path.basename(folder_path)
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                s3_key = os.path.join(target_folder_name, os.path.relpath(file_path, folder_path)).replace("\\",
                                                                                                           "/")  # 转换为正斜杠
                print(f"Uploading {s3_key} - {file_path}")
                self.put_file(s3_key, file_path)

    @catch_exceptions_decorator
    def delete_file(self, filename):
        """
        Delete a file from the specified S3 bucket.

        :param s3: S3 client object
        :param bucket_name: Name of the S3 bucket
        :param filename: Name of the file (key) to delete
        :return: Response from the delete operation
        """
        s3 = self.s3
        bucket_name = self.bucket_name

        try:
            response = s3.delete_object(
                Bucket=bucket_name,
                Key=filename,
            )
            print(f"File '{filename}' has been deleted from bucket '{bucket_name}'.")
            return response
        except Exception as e:
            print(f"Failed to delete {filename}: {str(e)}")
            return None

    @catch_exceptions_decorator
    def delete_folder(self, folder_name):
        """
        Delete all files within a specified folder (directory) in the S3 bucket.

        :param s3: S3 client object
        :param bucket_name: Name of the S3 bucket
        :param folder_name: Name of the folder (directory) to delete
        :return: Response from the delete operation
        """
        s3 = self.s3
        bucket_name = self.bucket_name

        try:
            # Ensure folder name ends with '/'
            if not folder_name.endswith('/'):
                folder_name += '/'

            # List all objects with the folder prefix
            objects_to_delete = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)

            # Check if there are any objects to delete
            if 'Contents' in objects_to_delete:
                delete_keys = [{'Key': obj['Key']} for obj in objects_to_delete['Contents']]

                # Delete the objects
                response = s3.delete_objects(
                    Bucket=bucket_name,
                    Delete={'Objects': delete_keys}
                )

                print(f"Folder '{folder_name}' and its contents have been deleted from bucket '{bucket_name}'.")
                return response
            else:
                print(f"Folder '{folder_name}' does not exist or is already empty.")
                return None

        except Exception as e:
            print(f"Failed to delete folder {folder_name}: {str(e)}")
            return None

    def create_folder(self, folder_name):
        """
        Create a folder (prefix) in the specified S3 bucket.

        :param folder_name: Name of the folder (prefix) to create
        :return: Response from the put_object operation
        """
        s3 = self.s3
        bucket_name = self.bucket_name

        # Ensure folder name ends with '/'
        if not folder_name.endswith('/'):
            folder_name += '/'

        try:
            response = s3.put_object(
                Bucket=bucket_name,
                Key=folder_name,
                Body=b''  # Empty body to create a "folder"
            )
            print(f"Folder '{folder_name}' has been created in bucket '{bucket_name}'.")
            return response
        except Exception as e:
            print(f"Failed to create folder {folder_name}: {str(e)}")
            return None

    # 搜索文件
    def search_file(self, keyword):
        """
        Search for a file in the specified S3 bucket by keyword.


        :param keyword: Keyword to search for
        :return: List of file items that match the keyword
        """
        s3 = self.s3
        bucket_name = self.bucket_name

        file_items = []
        response = s3.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in response:
            for obj in response['Contents']:
                file_key = obj['Key']
                if keyword in file_key:
                    file_size = obj['Size'] // 1024  # 转换为KB单位
                    file_url = s3.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': bucket_name, 'Key': file_key},
                        ExpiresIn=REDIS_TIMEOUT  # 预签名 URL 的有效期，单位为秒
                    )
                    file_items.append({'size': file_size, 'url': file_url, 'name': file_key})
        else:
            print("The bucket is empty or does not exist.")

        return file_items


def test_s3client():
    # 初始化S3Client
    s3_client = S3Client(
        access_key="RZAmQSrUij0dD9rzSMme",
        secret_key="L797b4OXAjh01frnRtoEpvPoqxjSsBi0HVakkc3R",
        bucket_name="images",
        end_point="http://pythond.cn:9000"
    )

    # 测试是否存在指定的bucket
    if not s3_client.have_bucket():
        raise Exception('Bucket does not exist')

    # 测试上传文件
    test_file = "test_upload.txt"
    with open(test_file, "w") as f:
        f.write("This is a test file for upload.")
    s3_client.put_file("test_upload.txt", test_file)
    print("Upload test file complete.")

    # 测试列出文件
    print("Listing files in the bucket:")
    s3_client.list_files()

    # 测试下载文件
    s3_client.download_file("test_upload.txt", "downloaded_test_file.txt")
    print("Download test file complete.")

    # 测试删除文件
    s3_client.delete_file("test_upload.txt")
    print("Delete test file complete.")

    # 测试上传文件夹
    test_folder = "test_folder"
    os.makedirs(test_folder, exist_ok=True)
    with open(os.path.join(test_folder, "file1.txt"), "w") as f:
        f.write("This is file 1 in the folder.")
    with open(os.path.join(test_folder, "file2.txt"), "w") as f:
        f.write("This is file 2 in the folder.")
    s3_client.upload_folder(test_folder)
    print("Upload test folder complete.")

    # 测试删除文件夹
    s3_client.delete_folder("test_folder")
    print("Delete test folder complete.")

    # 清理本地生成的测试文件和文件夹
    # os.remove(test_file)
    # os.remove("downloaded_test_file.txt")
    # os.remove(os.path.join(test_folder, "file1.txt"))
    # os.remove(os.path.join(test_folder, "file2.txt"))
    # os.rmdir(test_folder)

    print("All tests completed successfully.")

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import S3ConfigSerializer, FileUploadSerializer
from .models import S3Config
from .s3client import S3Client
from django.core.cache import cache


# 获取 S3 配置的 API
@api_view(['GET'])
def api_get_s3_config(request):
    try:
        config = S3Config.objects.latest('id')
        serializer = S3ConfigSerializer(config)
        return Response(serializer.data)
    except S3Config.DoesNotExist:
        return Response({'detail': 'S3 配置未设置！'}, status=status.HTTP_404_NOT_FOUND)


# 配置 S3 的 API
@api_view(['POST'])
def api_configure_s3(request):
    serializer = S3ConfigSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "S3 配置已保存成功！"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 文件上传 API
@api_view(['POST'])
def api_upload_files(request):
    config = S3Config.objects.latest('id')
    s3_client = S3Client(config.access_key, config.secret_key, config.bucket_name, config.end_point)

    files = request.FILES.getlist('file')
    if not files:
        return Response({"detail": "没有文件上传！"}, status=status.HTTP_400_BAD_REQUEST)

    for file in files:
        result = s3_client.put_file(file.name, file)
        if not result:
            return Response({"detail": f"文件 '{file.name}' 上传失败！"}, status=status.HTTP_400_BAD_REQUEST)

    # 清除缓存
    cache.delete('file_list')
    return Response({"message": "文件上传成功！"}, status=status.HTTP_200_OK)


# 获取文件列表 API
@api_view(['GET'])
def api_list_files(request):
    config = S3Config.objects.latest('id')
    s3_client = S3Client(config.access_key, config.secret_key, config.bucket_name, config.end_point)

    list_files = cache.get('file_list')
    if list_files is None:
        try:
            list_files = s3_client.list_files(config.bucket_name)
            cache.set('file_list', list_files, timeout=300)
        except Exception as e:
            return Response({"detail": f"获取文件列表失败：{e}"}, status=status.HTTP_400_BAD_REQUEST)

    return Response(list_files)


# 搜索文件 API
@api_view(['POST'])
def api_search_files(request):
    config = S3Config.objects.latest('id')
    s3_client = S3Client(config.access_key, config.secret_key, config.bucket_name, config.end_point)

    keyword = request.data.get('keyword')
    if not keyword:
        return Response({"detail": "请输入搜索关键字！"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        list_files = s3_client.search_file(keyword,config.bucket_name)
        return Response(list_files)
    except Exception as e:
        return Response({"detail": f"搜索失败：{e}"}, status=status.HTTP_400_BAD_REQUEST)


# 删除文件 API
@api_view(['DELETE'])
def api_delete_file(request):
    config = S3Config.objects.latest('id')
    s3_client = S3Client(config.access_key, config.secret_key, config.bucket_name, config.end_point)

    file_name = request.data.get('file_name')
    if not file_name:
        return Response({"detail": "缺少文件名！"}, status=status.HTTP_400_BAD_REQUEST)

    result = s3_client.delete_file(file_name)
    if result:
        cache.delete('file_list')
        return Response({"message": f"文件 '{file_name}' 已成功删除！"}, status=status.HTTP_200_OK)
    else:
        return Response({"detail": f"删除文件 '{file_name}' 失败！"}, status=status.HTTP_400_BAD_REQUEST)

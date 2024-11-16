from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect

from .forms import S3ConfigForm, FileUploadForm
from .models import S3Config
from .s3client import S3Client
from django.core.cache import cache
from PIL import Image
import io
import cProfile
import pstats

REDIS_TIMEOUT = 60 * 60 * 72 # 缓存过期时间，72小时

def compress_image(file, quality=70):
    img = Image.open(file)
    img = img.convert("RGB")  # 转换为 RGB 模式
    byte_io = io.BytesIO()
    img.save(byte_io, 'WebP', quality=quality)  # 使用 WebP 格式
    byte_io.seek(0)
    return byte_io


# 请将这些变量替换为你的实际值
# ACCESS_KEY = 'iHlsYc77oCHdGTWwPF7I'
# SECRET_KEY = 'MjXHKX90GYZ7xRgr1kWG1d2gyd89EcVzmglg2bvz'
# BUCKET_NAME = 'mlhz'
# END_POINT = 'http://47.113.186.186:9000'

def get_s3_config():
    try:
        return S3Config.objects.latest('id')
    except S3Config.DoesNotExist:
        return None


def configure_s3_view(request):
    if request.method == 'POST':
        form = S3ConfigForm(request.POST)
        if form.is_valid():
            config = form.save()

            messages.success(request, "S3 配置已保存成功！")
            return redirect('cloud:file_list')
    else:
        # GET 请求时，检查是否已有配置数据
        try:
            config = S3Config.objects.latest('id')
            form = S3ConfigForm(instance=config)
        except S3Config.DoesNotExist:
            form = S3ConfigForm()

    return render(request, 'cloud/configure_s3.html', {'form': form})


def file_list_view(request):
    config = get_s3_config()
    if not config:
        messages.error(request, "S3 配置未设置！")
        return redirect('cloud:configure_s3')

    s3_client = S3Client(
        config.access_key,
        config.secret_key,
        config.bucket_name,
        config.end_point
    )

    # 获取文件列表并缓存
    list_files = cache.get('file_list')
    if list_files is None:
        try:
            list_files = s3_client.list_files()
            # list_files数据格式：[{'size': file_size, 'url': file_url, 'name': file_key},...]
            cache.set('file_list', list_files, timeout=REDIS_TIMEOUT)  # 缓存文件列表 1 小时
        except Exception as e:
            messages.error(request, f"获取文件列表失败：{e}")
            return redirect('cloud:file_list')

    # 上传文件后增量更新缓存
    if request.method == 'POST':
        files = request.FILES.getlist('file')
        if not files:
            messages.error(request, "没有文件上传！")
            return redirect('cloud:file_list')

        # 处理每个文件
        for file in files:
            # 压缩图片
            compressed_file = compress_image(file)
            result = s3_client.put_file(file.name, compressed_file)
            if result:
                messages.success(request, f"文件 '{file.name}' 上传成功！")
                new_file = s3_client.get_file_info_by_name(file.name)

                # 上传成功后更新缓存
                list_files.append(new_file)
                cache.set('file_list', list_files, timeout=REDIS_TIMEOUT)  # 60小时缓存
            else:
                messages.error(request, f"文件 '{file.name}' 上传失败！")

        return redirect('cloud:file_list')

    # 分页处理
    page = request.GET.get('page', 1)
    paginator = Paginator(list_files, 8)
    try:
        files = paginator.page(page)
    except PageNotAnInteger:
        files = paginator.page(1)
    except EmptyPage:
        files = paginator.page(paginator.num_pages)

    return render(request, 'cloud/index.html', {
        'files': files,
    })


def search(request):
    config = get_s3_config()
    if not config:
        messages.error(request, "S3 配置未设置！")
        return redirect('cloud:configure_s3')

    s3_client = S3Client(
        config.access_key,
        config.secret_key,
        config.bucket_name,
        config.end_point
    )

    keyword = request.POST.get('keyword')
    if not keyword:
        messages.error(request, "请输入搜索关键字！")
        return redirect('cloud:file_list')

    try:
        list_files = s3_client.search_file(keyword)
    except Exception as e:
        messages.error(request, f"搜索失败：{e}")
        return redirect('cloud:file_list')

    return render(request, 'cloud/index.html', {'files': list_files})


def delete_file_view(request):
    config = get_s3_config()
    if not config:
        messages.error(request, "S3 配置未设置！")
        return redirect('cloud:configure_s3')

    s3_client = S3Client(
        config.access_key,
        config.secret_key,
        config.bucket_name,
        config.end_point
    )

    file_name = request.POST.get('file_name')
    result = s3_client.delete_file(file_name)

    if result:
        # 删除成功后从缓存中移除该文件
        list_files = cache.get('file_list')
        if list_files:
            list_files = [f for f in list_files if f['name'] != file_name]
            cache.set('file_list', list_files, timeout=REDIS_TIMEOUT)
        messages.success(request, f"文件 '{file_name}' 已成功删除！")
    else:
        messages.error(request, f"删除文件 '{file_name}' 失败！")

    return redirect('cloud:file_list')

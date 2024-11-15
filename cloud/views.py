from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect

from .forms import S3ConfigForm, FileUploadForm
from .models import S3Config
from .s3client import S3Client
from django.core.cache import cache


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

    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            result = s3_client.put_file(file.name, file)
            if result:
                messages.success(request, f"文件 '{file.name}' 已上传成功！")
                cache.delete('file_list')  # 清除缓存，确保最新文件
            else:
                messages.error(request, f"文件 '{file.name}' 上传失败！")
        else:
            messages.error(request, "文件未选择或文件大小超出限制！")
        return redirect('cloud:file_list')

    else:
        form = FileUploadForm()

    # 获取文件列表并缓存
    list_files = cache.get('file_list')
    if list_files is None:
        try:
            list_files = s3_client.list_files()
            cache.set('file_list', list_files, timeout=300)
        except Exception as e:
            messages.error(request, f"获取文件列表失败：{e}")
            return redirect('cloud:file_list')

    # 分页处理
    page = request.GET.get('page', 1)  # 获取当前页码，默认为第 1 页
    paginator = Paginator(list_files, 10)  # 每页显示 10 个文件
    try:
        files = paginator.page(page)
    except PageNotAnInteger:
        files = paginator.page(1)  # 如果页码不是整数，则显示第 1 页
    except EmptyPage:
        files = paginator.page(paginator.num_pages)  # 如果页码超出范围，则显示最后一页

    return render(request, 'cloud/file_list.html', {
        'files': files,  # 分页后的文件列表
        'form': form
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

    return render(request, 'cloud/file_list.html', {'files': list_files})


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
        # 清除缓存，以确保文件列表是最新的
        cache.delete('file_list')
        messages.success(request, f"文件 '{file_name}' 已成功删除！")
    else:
        messages.error(request, f"删除文件 '{file_name}' 失败！")

    return redirect('cloud:file_list')

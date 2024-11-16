from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .forms import S3ConfigForm
from .models import S3Config
from .s3client import S3Client
from django.core.cache import cache
from PIL import Image
import io
from django.contrib.auth import authenticate, login
from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages

REDIS_TIMEOUT = 60 * 60 * 72 # 缓存过期时间，72小时

def compress_image(file, quality=70):
    img = Image.open(file)
    img = img.convert("RGB")  # 转换为 RGB 模式
    byte_io = io.BytesIO()
    img.save(byte_io, 'WebP', quality=quality)  # 使用 WebP 格式
    byte_io.seek(0)
    return byte_io


def user_login(request):
    # 如果用户已经登录，跳转到主页
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # 尝试认证用户
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # 获取登录前的跳转地址，若没有提供，则跳转到主页
            next_url = request.GET.get('next', 'index')

            return redirect(next_url)  # 登录成功后跳转到指定页面
        else:
            messages.error(request, '用户名或密码错误')

    return render(request, 'cloud/login.html')  # 渲染登录页面

def get_s3_config(request):
    try:
        return request.user.s3_config  # 获取当前用户的 S3 配置
    except S3Config.DoesNotExist:
        return None

@login_required  # 确保用户已登录
def configure_s3_view(request):
    if request.method == 'POST':
        form = S3ConfigForm(request.POST)
        if form.is_valid():
            config, created = S3Config.objects.update_or_create(
                user=request.user,  # 更新或创建当前用户的配置
                defaults=form.cleaned_data  # 使用表单数据更新配置
            )

            return redirect('index')
    else:
        # GET 请求时，检查是否已有配置数据
        config = get_s3_config(request)
        if config:
            form = S3ConfigForm(instance=config)
        else:
            form = S3ConfigForm()

    return render(request, 'cloud/configure_s3.html', {'form': form})

@login_required  # 确保用户已登录
def file_list_view(request):
    config = get_s3_config(request)  # 使用当前用户的配置
    if not config:
        messages.error(request, "S3 配置未设置！")
        return redirect('cloud:configure_s3')  # 配置未设置时跳转到配置页面

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
            return redirect('index')

    # 上传文件后增量更新缓存
    if request.method == 'POST':
        files = request.FILES.getlist('file')
        if not files:
            messages.error(request, "没有文件上传！")
            return redirect('index')

        # 处理每个文件
        for file in files:
            # 压缩图片
            compressed_file = compress_image(file)
            result = s3_client.put_file(file.name, compressed_file)
            if result:

                new_file = s3_client.get_file_info_by_name(file.name)

                # 上传成功后更新缓存
                list_files.append(new_file)
                cache.set('file_list', list_files, timeout=REDIS_TIMEOUT)  # 60小时缓存
            else:
                messages.error(request, f"文件 '{file.name}' 上传失败！")

        return redirect('index')

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

@login_required  # 确保用户已登录
def search(request):
    config = get_s3_config(request)  # 使用当前用户的配置
    if not config:
        messages.error(request, "S3 配置未设置！")
        return redirect('cloud:configure_s3')  # 配置未设置时跳转到配置页面

    s3_client = S3Client(
        config.access_key,
        config.secret_key,
        config.bucket_name,
        config.end_point
    )

    keyword = request.POST.get('keyword')
    if not keyword:
        messages.error(request, "请输入搜索关键字！")
        return redirect('index')

    try:
        list_files = s3_client.search_file(keyword)
    except Exception as e:
        messages.error(request, f"搜索失败：{e}")
        return redirect('index')

    return render(request, 'cloud/index.html', {'files': list_files})

@login_required  # 确保用户已登录
def delete_file_view(request):
    config = get_s3_config(request)  # 使用当前用户的配置
    if not config:
        messages.error(request, "S3 配置未设置！")
        return redirect('cloud:configure_s3')  # 配置未设置时跳转到配置页面

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

    else:
        messages.error(request, f"删除文件 '{file_name}' 失败！")

    return redirect('index')

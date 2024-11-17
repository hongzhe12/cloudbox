// 创建 Spin.js 动画实例
var opts = {
    lines: 13, // 花瓣数量
    length: 28, // 花瓣长度
    width: 14, // 花瓣宽度
    radius: 42, // 花瓣到中心点的距离
    scale: 0.25, // 缩放比例
    corners: 1, // 圆角程度
    color: '#000', // 颜色
    speed: 1, // 动画速度
    trail: 60, // 每个花瓣的消失时间
    shadow: false, // 是否显示阴影
    hwaccel: false, // 是否开启硬件加速
    position: 'absolute' // 设置位置
};

var spinner = new Spinner(opts);

// 监听上传表单的提交事件
document.getElementById('uploadForm').onsubmit = function (event) {
    event.preventDefault();  // 阻止表单提交

    // 显示加载动画
    document.getElementById('loadingContainer').style.display = 'block';
    spinner.spin(document.getElementById('spinner'));

    // 创建一个新的 FormData 对象
    var formData = new FormData(this);

    // 发送 AJAX 请求上传文件
    var xhr = new XMLHttpRequest();
    xhr.open('POST', this.action, true);
    xhr.setRequestHeader('X-CSRFToken', '{{ csrf_token }}');  // 添加 CSRF Token

    xhr.onload = function () {
        if (xhr.status === 200) {
            // 上传成功，隐藏加载动画
            document.getElementById('loadingContainer').style.display = 'none';
            // 使用 SweetAlert2 显示上传成功提示
            Swal.fire({
                icon: 'success',
                title: '文件上传成功',
                text: '您的文件已经成功上传。',
                confirmButtonText: '确定'
            }).then(() => {
                location.reload();  // 刷新页面以更新文件列表
            });
        } else {
            // 上传失败，隐藏加载动画并显示错误消息
            document.getElementById('loadingContainer').style.display = 'none';
            // 使用 SweetAlert2 显示上传失败提示
            Swal.fire({
                icon: 'error',
                title: '文件上传失败',
                text: '请重试。',
                confirmButtonText: '确定'
            });
        }
    };

    // 上传文件
    xhr.send(formData);
};

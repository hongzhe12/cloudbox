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
        // 上传完成后，隐藏加载动画
        document.getElementById('loadingContainer').style.display = 'none';
    
        if (xhr.status === 200) {
            // 解析后端返回的 JSON 响应
            var response = JSON.parse(xhr.responseText);
    
            // 使用 SweetAlert2 显示相应的弹窗
            Swal.fire({
                icon: response.icon || 'info',  // 默认图标为 'info'
                title: response.title || '提示',  // 默认标题为 '提示'
                text: response.text || '操作结果未知',  // 默认文本
                confirmButtonText: response.confirmButtonText || '确定'  // 默认按钮文本
            }).then(() => {
                // 根据需求决定是否刷新页面或执行其他操作
                if (xhr.status === 200 && response.icon === 'success') {
                    location.reload();  // 刷新页面以更新文件列表
                }
            });
        } 
        
        else {
            // 网络错误或其他错误，显示默认的错误提示
            document.getElementById('loadingContainer').style.display = 'none';
            Swal.fire({
                icon: 'error',
                title: '上传失败',
                text: '网络错误或服务器问题，请稍后重试。',
                confirmButtonText: '确定'
            });
        }
    };

    // 上传文件
    xhr.send(formData);
};

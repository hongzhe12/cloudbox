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

// // 监听上传表单的提交事件
// document.getElementById('uploadForm').onsubmit = function (event) {
//     event.preventDefault();  // 阻止表单提交

//     // 显示加载动画
//     document.getElementById('loadingContainer').style.display = 'block';
//     spinner.spin(document.getElementById('spinner'));

//     // 创建一个新的 FormData 对象
//     var formData = new FormData(this);

//     // 发送 AJAX 请求上传文件
//     var xhr = new XMLHttpRequest();
//     xhr.open('POST', this.action, true);
//     xhr.setRequestHeader('X-CSRFToken', '{{ csrf_token }}');  // 添加 CSRF Token

//     xhr.onload = function () {
//         // 上传完成后，隐藏加载动画
//         document.getElementById('loadingContainer').style.display = 'none';
    
//         if (xhr.status === 200) {
//             // 解析后端返回的 JSON 响应
//             var response = JSON.parse(xhr.responseText);
    
//             // 使用 SweetAlert2 显示相应的弹窗
//             Swal.fire({
//                 icon: response.icon || 'info',  // 默认图标为 'info'
//                 title: response.title || '提示',  // 默认标题为 '提示'
//                 text: response.text || '操作结果未知',  // 默认文本
//                 confirmButtonText: response.confirmButtonText || '确定'  // 默认按钮文本
//             }).then(() => {
//                 // 根据需求决定是否刷新页面或执行其他操作
//                 if (xhr.status === 200 && response.icon === 'success') {
//                     location.reload();  // 刷新页面以更新文件列表
//                 }
//             });
//         } 
        
//         else {
//             // 网络错误或其他错误，显示默认的错误提示
//             document.getElementById('loadingContainer').style.display = 'none';
//             Swal.fire({
//                 icon: 'error',
//                 title: '上传失败',
//                 text: '网络错误或服务器问题，请稍后重试。',
//                 confirmButtonText: '确定'
//             });
//         }
//     };

//     // 上传文件
//     xhr.send(formData);
// };


//   // 使用事件委托来为删除按钮绑定事件
//   document.querySelectorAll('.delete-button').forEach(function(deleteButton) {
//     deleteButton.addEventListener('click', function(event) {
//         event.preventDefault();  // 阻止表单默认提交行为

//         var form = event.target.closest('form');  // 获取删除按钮所在的表单
//         var fileName = form.querySelector('input[name="file_name"]').value;  // 获取文件名

//         // 使用 SweetAlert2 弹出确认框
//         Swal.fire({
//             title: '确认删除？',
//             text: '删除后无法恢复！',
//             icon: 'warning',
//             showCancelButton: true,
//             confirmButtonText: '删除',
//             cancelButtonText: '取消',
//             reverseButtons: true
//         }).then((result) => {
//             if (result.isConfirmed) {
//                 // 用户确认删除后，提交表单
//                 var xhr = new XMLHttpRequest();
//                 xhr.open('POST', form.action, true);
//                 xhr.setRequestHeader('X-CSRFToken', form.querySelector('[name=csrfmiddlewaretoken]').value);  // 设置 CSRF token
//                 xhr.onreadystatechange = function() {
//                     if (xhr.readyState === 4) {  // 请求完成
//                         if (xhr.status === 200) {
//                             // 请求成功，解析响应数据
//                             var data = JSON.parse(xhr.responseText);

//                             // 使用 SweetAlert2 显示后端返回的弹窗
//                             Swal.fire({
//                                 icon: data.icon,
//                                 title: data.title,
//                                 text: data.text,
//                                 confirmButtonText: data.confirmButtonText
//                             }).then(() => {
//                                 if (data.icon === 'success') {
//                                     location.reload();  // 删除成功后刷新页面
//                                 }
//                             });
//                         } else {
//                             // 请求失败，显示错误弹窗
//                             Swal.fire({
//                                 icon: 'error',
//                                 title: '删除失败',
//                                 text: '文件删除过程中出现问题，请稍后重试。',
//                                 confirmButtonText: '确定'
//                             });
//                         }
//                     }
//                 };

//                 xhr.send(new FormData(form));  // 发送表单数据
//             }
//         });
//     });
// });

// 通用的 AJAX 请求函数
function sendAjaxRequest(method, url, formData, csrfToken, onSuccess, onError) {
    var xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    xhr.setRequestHeader('X-CSRFToken', csrfToken);

    xhr.onload = function () {
        if (xhr.status === 200) {
            onSuccess(JSON.parse(xhr.responseText));
        } else {
            onError(xhr.status, xhr.responseText);
        }
    };

    xhr.onerror = function () {
        onError(xhr.status, xhr.responseText);
    };

    xhr.send(formData);
}

// 显示 SweetAlert2 弹窗
function showAlert(response) {
    Swal.fire({
        icon: response.icon || 'info',
        title: response.title || '提示',
        text: response.text || '操作结果未知',
        confirmButtonText: response.confirmButtonText || '确定'
    }).then(() => {
        if (response.icon === 'success') {
            location.reload();  // 刷新页面
        }
    });
}

// 表单上传处理
document.getElementById('uploadForm').onsubmit = function (event) {
    event.preventDefault();  // 阻止表单提交

    // 显示加载动画
    document.getElementById('loadingContainer').style.display = 'block';
    spinner.spin(document.getElementById('spinner'));

    var formData = new FormData(this);
    var csrfToken = '{{ csrf_token }}';  // 获取 CSRF Token

    sendAjaxRequest('POST', this.action, formData, csrfToken, function(response) {
        // 上传完成后，隐藏加载动画
        document.getElementById('loadingContainer').style.display = 'none';
        showAlert(response);  // 显示返回的弹窗
    }, function(status, responseText) {
        document.getElementById('loadingContainer').style.display = 'none';
        Swal.fire({
            icon: 'error',
            title: '上传失败',
            text: '网络错误或服务器问题，请稍后重试。',
            confirmButtonText: '确定'
        });
    });
};

// 删除按钮处理
document.querySelectorAll('.delete-button').forEach(function(deleteButton) {
    deleteButton.addEventListener('click', function(event) {
        event.preventDefault();  // 阻止默认行为

        var form = event.target.closest('form');  // 获取删除按钮所在的表单
        var csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;  // 获取 CSRF token

        // 使用 SweetAlert2 弹出确认框
        Swal.fire({
            title: '确认删除？',
            text: '删除后无法恢复！',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: '删除',
            cancelButtonText: '取消',
            reverseButtons: true
        }).then((result) => {
            if (result.isConfirmed) {
                var formData = new FormData(form);
                sendAjaxRequest('POST', form.action, formData, csrfToken, function(response) {
                    showAlert(response);  // 显示返回的弹窗
                }, function(status, responseText) {
                    Swal.fire({
                        icon: 'error',
                        title: '删除失败',
                        text: '文件删除过程中出现问题，请稍后重试。',
                        confirmButtonText: '确定'
                    });
                });
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function () {
    console.log('Document is ready.');

    var fileDetailModal = document.getElementById('fileDetailModal');
    if (!fileDetailModal) {
        console.error('Modal element with id "fileDetailModal" not found.');
        return;
    }
    console.log('Modal element found:', fileDetailModal);

    fileDetailModal.addEventListener('show.bs.modal', function (event) {
        console.log('Modal show event triggered:', event);

        var button = event.relatedTarget;
        if (!button) {
            console.error('No related target found for the modal show event.');
            return;
        }
        console.log('Triggering button element:', button);

        var modal = fileDetailModal;

        var fileName = button.getAttribute('data-name') || 'N/A';
        var fileSize = button.getAttribute('data-size') || 'N/A';
        var fileModified = button.getAttribute('data-modified') || 'N/A';
        var fileEtag = button.getAttribute('data-etag') || 'N/A';
        var fileStorage = button.getAttribute('data-storage') || 'N/A';

        // 获取隐藏的文件访问 URL（不在前端展示）
        var fileUrl = button.getAttribute('data-url');
        console.log('File details:', { fileName, fileSize, fileModified, fileEtag, fileStorage, fileUrl });

        modal.querySelector('#modalFileName').textContent = fileName;
        modal.querySelector('#modalFileSize').textContent = fileSize;
        modal.querySelector('#modalFileModified').textContent = fileModified;
        modal.querySelector('#modalFileEtag').textContent = fileEtag;
        modal.querySelector('#modalFileStorage').textContent = fileStorage;

        // 仅显示文件名，不显示 URL
        var fileUrlLink = modal.querySelector('#modalFileUrl');
        fileUrlLink.textContent = '点击下载'; // 显示下载按钮文本
        fileUrlLink.href = '/download/file/' + encodeURIComponent(fileName); // 后端提供下载接口
        fileUrlLink.title = '点击下载文件'; // 添加工具提示

        console.log('Modal content updated.');
    });
});




// 初始化 Fancybox
$(document).ready(function () {
    $('[data-fancybox="gallery"]').fancybox({
        buttons: [
            'zoom',
            'share',
            'slideShow',
            'fullScreen',
            'download',
            'thumbs',
            'close'
        ],
        loop: true,  // 允许循环查看图片
        protect: true  // 禁止右键保存图片
    });
});


// 获取表单和加载动画元素
    const form = document.getElementById('uploadForm');
    const loading = document.getElementById('loading');

    // 提交表单时显示加载动画
    form.addEventListener('submit', function (event) {
        // 显示加载动画
        loading.style.display = 'block';

        // 防止默认表单提交行为，使用 AJAX 提交
        event.preventDefault();

        // 创建 FormData 对象
        const formData = new FormData(form);

        // 使用 AJAX 提交文件
        fetch(form.action, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // 上传完成后隐藏加载动画
            loading.style.display = 'none';
            // 可选：根据返回的数据进行处理，如显示成功信息等
            if (data.success) {
                alert("文件上传成功！");
            } else {
                alert("上传失败！");
            }
        })
        .catch(error => {
            loading.style.display = 'none';
            console.error('Error uploading file:', error);
            alert("上传失败！");
        });
    });



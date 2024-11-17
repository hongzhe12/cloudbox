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
        console.log('File details:', {fileName, fileSize, fileModified, fileEtag, fileStorage, fileUrl});

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
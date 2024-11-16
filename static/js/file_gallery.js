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

import io
from PIL import Image


def compress_image(file_content, quality=70):
    # 将字节内容转换为 BytesIO 对象，使其像文件一样被打开
    file = io.BytesIO(file_content)

    # 使用 PIL 打开图片
    img = Image.open(file)
    img = img.convert("RGB")  # 转换为 RGB 模式

    # 创建一个 BytesIO 对象来保存压缩后的图像
    byte_io = io.BytesIO()

    # 使用 WebP 格式保存压缩后的图像
    img.save(byte_io, 'WebP', quality=quality)
    byte_io.seek(0)  # 移动到文件的开头

    return byte_io
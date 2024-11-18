# 使用官方 Python 运行时作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /code

# 设置 pip 国内源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config set global.no-cache-dir true

# 复制依赖文件并安装
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# 复制项目源代码
COPY . .

# 设置环境变量
ENV DJANGO_SETTINGS_MODULE=CloudBox.settings



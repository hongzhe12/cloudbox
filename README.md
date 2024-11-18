# CloudBox  

CloudBox 是一个基于 Django 的云存储管理平台，用户可以方便地将文件上传至 AWS S3 或兼容的存储服务，支持文件列表显示、搜索和删除等功能。本项目注重用户体验，采用异步任务、缓存优化等技术实现高效的文件管理，同时美化了提示框和加载动画，提供现代化的用户界面。  

## 项目特点  

### 1. 功能丰富  
- **文件上传**：支持通过表单上传多个文件，异步处理提高响应速度。  
- **文件管理**：提供文件列表的分页展示，并支持搜索、删除功能。  
- **用户配置**：每个用户可独立配置 S3 存储信息，确保隔离性和安全性。  

### 2. 优化性能  
- **缓存机制**：利用 Redis 缓存文件列表，减少 S3 API 的调用，提升系统性能。  
- **异步任务**：使用 Celery 将文件上传操作放入后台任务队列，避免阻塞用户操作。  

### 3. 用户友好的交互体验  
- **加载动画**：采用 Spin.js 提供加载动画，在文件上传过程中显示动态反馈。  
- **弹窗提示**：集成 SweetAlert2 美化提示框，用于显示文件上传结果、错误消息等。  

### 4. 高扩展性  
- **分层设计**：采用经典的 MVC 模式，代码易于扩展和维护。  
- **性能分析**：集成 cProfile 和 pstats，用于分析性能瓶颈，便于优化关键路径。  

---

## 技术栈  
- **后端框架**：Django  
- **任务队列**：Celery  
- **缓存**：Redis  
- **前端交互**：HTML + CSS + JavaScript  
  - Spin.js：加载动画  
  - SweetAlert2：美化提示框  
- **存储服务**：AWS S3（或兼容的 S3 服务）  

---

## 安装与运行  

### 1. 克隆项目  
```bash  
git clone https://github.com/yourusername/cloudbox.git  
cd cloudbox  
```  

### 2. 安装依赖  
确保你安装了 Python 和 pip，运行以下命令安装依赖：  
```bash  
pip install -r requirements.txt  
```  

### 3. 配置环境变量  
在项目根目录创建 `.env` 文件，并配置以下变量：  
```env  
SECRET_KEY=your_django_secret_key  
DEBUG=True  
AWS_ACCESS_KEY=your_aws_access_key  
AWS_SECRET_KEY=your_aws_secret_key  
AWS_BUCKET_NAME=your_s3_bucket_name  
AWS_ENDPOINT_URL=your_s3_endpoint_url  # 如果使用兼容的 S3 服务  
```  

### 4. 配置 Redis  
确保 Redis 服务运行，并在 `settings.py` 中配置 Redis 缓存：  
```python  
CACHES = {  
    'default': {  
        'BACKEND': 'django_redis.cache.RedisCache',  
        'LOCATION': 'redis://127.0.0.1:6379/1',  
        'OPTIONS': {  
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',  
        }  
    }  
}  
```  

### 5. 启动 Celery  
运行以下命令启动 Celery worker：  
```bash  
celery -A cloudbox worker --loglevel=info  
```  

### 6. 启动开发服务器  
```bash  
python manage.py runserver  
```  

---

## 使用方法  

1. **登录**：注册并登录到系统。  
2. **配置 S3 信息**：在设置页面填写你的 S3 存储配置（访问密钥、密钥 ID、存储桶名称等）。  
3. **文件管理**：  
   - 上传文件至存储桶。  
   - 在文件列表中查看、搜索和删除文件。  

---

## 项目结构  

```plaintext  
cloudbox/  
├── cloud/                 # 应用目录  
│   ├── forms.py           # 表单定义  
│   ├── models.py          # 数据模型  
│   ├── views.py           # 视图函数  
│   ├── s3client.py        # S3 客户端封装  
│   ├── tasks.py           # Celery 任务定义  
├── templates/             # HTML 模板  
│   └── cloud/             # 应用相关模板  
├── static/                # 静态文件（JS、CSS）  
├── manage.py              # Django 项目入口  
└── requirements.txt       # 项目依赖  
```  

---

## 未来规划  

1. 支持多用户协作功能，提升团队使用体验。  
2. 集成文件预览功能，支持常见格式的在线预览。  
3. 增加文件分类与标签功能，便于用户管理大批量文件。  

---

## 贡献  
欢迎对 CloudBox 提交建议或贡献代码！请在提交 PR 前阅读项目的贡献指南。  

---  

希望这份 README 满足你的需求！如果有其他补充或改动，请告诉我！
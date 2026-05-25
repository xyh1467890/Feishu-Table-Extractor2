# 飞书多维表格元数据工具

这是一个 Django + Vue 3 Web 应用，用于获取飞书多维表格的元数据。

## 项目结构

```
table_meta_data_django+vue/
├── backend/              # Django 后端
│   ├── apps/            # Django 应用
│   │   └── api/        # API 应用
│   ├── config/          # Django 项目配置
│   ├── static/          # 静态文件
│   ├── templates/       # 模板文件
│   └── manage.py
├── frontend/            # Vue 3 前端
│   ├── public/          # 公共资源
│   ├── src/
│   │   ├── assets/      # 资源文件
│   │   ├── components/  # 组件
│   │   ├── api/        # API 调用
│   │   └── App.vue
│   └── package.json
└── README.md
```

## 快速开始

### 后端启动

1. 进入后端目录：
```bash
cd backend
```

2. 创建虚拟环境（可选）：
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 运行数据库迁移：
```bash
python manage.py migrate
```

5. 启动开发服务器：
```bash
python manage.py runserver
```

后端将在 http://localhost:8000 运行

### 前端启动

1. 进入前端目录：
```bash
cd frontend
```

2. 安装依赖：
```bash
npm install
```

3. 启动开发服务器：
```bash
npm run dev
```

前端将在 http://localhost:3000 运行

## 功能特性

- 支持多种认证方式：Token、OAuth、Cookie
- 获取飞书多维表格的元数据
- 支持导出 JSON 格式数据
- 响应式设计，适配各种屏幕
- 搜索和高亮功能

## API 接口

### POST /api/fetch/

获取飞书多维表格数据

**请求体：**
```json
{
  "auth_type": "token",
  "auth_data": "your_user_token",
  "feishu_url": "https://xxx.feishu.cn/base/xxx",
  "fetch_records": true
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "base_token": "xxx",
    "tables": [...]
  }
}
```

### GET /api/health/

健康检查接口

## 注意事项

- 请确保后端和前端同时运行
- 前端通过代理将 API 请求转发到后端
- Token 方式是推荐的认证方式，功能最完整

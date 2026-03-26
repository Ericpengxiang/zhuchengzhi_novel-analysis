# 小说数据分析可视化系统

## 运行程序

### 1. 环境要求

- Python 3.8+
- MySQL 5.7+ 或 MySQL 8.0+
- MySQL账号：root/root
- 数据库名：novel_analysis

### 2. 安装依赖

```bash
cd E:\PyCharm\PythonProject\代写\小说系统\mack
pip install -r requirements.txt
```

### 3. 配置数据库

确保MySQL服务已启动，数据库 `novel_analysis` 已创建。

如果没有数据，先运行爬虫脚本采集数据：

```bash
cd ../小数采集
python faloo_spider.py
```

### 4. 启动开发服务器

```bash
cd E:\PyCharm\PythonProject\代写\小说系统\mack
python manage.py runserver 8000
```

### 5. 访问系统

打开浏览器访问：

- **首页**：http://127.0.0.1:8000/
- **仪表盘**：http://127.0.0.1:8000/dashboard/
- **数据浏览**：http://127.0.0.1:8000/data-overview/
- **管理后台**：http://127.0.0.1:8000/admin/

### 6. 停止服务器

在运行服务器的终端中按 `Ctrl + C` 停止服务器。

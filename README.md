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

## 协同过滤优化算法尝试版（新增）

- 推荐对比页面：`http://127.0.0.1:8000/recommend/`
- 原推荐接口：`GET /api/novel/recommend/?mode=standard`
- 优化推荐接口：`GET /api/novel/recommend/optimized/?alpha=0.6&top_n=5&threshold=0.2&top_k=6`
- 对比接口：`GET /api/novel/recommend/?mode=compare`

### 初始化最小实验数据

```bash
python manage.py seed_data
```

### 运行轻量实验脚本

```bash
python manage.py shell < scripts/eval_cf_optimize.py
```

输出包含 Precision / Recall / F1 的原推荐与优化推荐对比，可用于论文实验截图。

### 6. 停止服务器

在运行服务器的终端中按 `Ctrl + C` 停止服务器。

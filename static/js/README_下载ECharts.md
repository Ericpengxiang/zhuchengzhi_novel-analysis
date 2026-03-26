# ECharts 下载说明

## 问题
CDN无法访问，导致图表不显示。

## 解决步骤

### 步骤1：下载 ECharts 文件

**方法A：浏览器下载（推荐）**
1. 打开浏览器，访问以下任一链接：
   - https://cdn.bootcdn.net/ajax/libs/echarts/5.4.3/echarts.min.js
   - https://unpkg.com/echarts@5/dist/echarts.min.js
   - https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js

2. 页面会显示JavaScript代码，按 `Ctrl+S` 保存文件
3. 保存时文件名改为：`echarts.min.js`
4. 保存位置：`小说系统/mack/static/js/echarts.min.js`

**方法B：使用Python脚本下载**
在项目根目录运行：
```python
import urllib.request
url = "https://cdn.bootcdn.net/ajax/libs/echarts/5.4.3/echarts.min.js"
urllib.request.urlretrieve(url, "小说系统/mack/static/js/echarts.min.js")
print("下载完成！")
```

### 步骤2：修改代码使用本地文件

打开 `templates/novel/dashboard.html`，找到第129行左右：

**当前代码（使用CDN）：**
```html
<script src="https://cdn.bootcdn.net/ajax/libs/echarts/5.4.3/echarts.min.js"></script>
```

**改为（使用本地文件）：**
```html
<script src="{% static 'js/echarts.min.js' %}"></script>
```

### 步骤3：刷新页面

1. 保存文件后，刷新浏览器页面（Ctrl+F5强制刷新）
2. 打开浏览器控制台（F12），确认没有 `echarts is not defined` 错误
3. 图表应该正常显示了

## 验证

下载完成后，确认文件存在：
- 路径：`小说系统/mack/static/js/echarts.min.js`
- 文件大小：约 700KB-1MB
- 如果文件存在，修改代码后刷新页面即可







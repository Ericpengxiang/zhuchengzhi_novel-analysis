"""
自动下载 ECharts 文件到本地
"""
import urllib.request
import os
from pathlib import Path

# 获取当前脚本所在目录
script_dir = Path(__file__).parent
target_file = script_dir / 'static' / 'js' / 'echarts.min.js'

# 确保目录存在
target_file.parent.mkdir(parents=True, exist_ok=True)

# CDN地址列表（按优先级）
cdn_urls = [
    'https://cdn.bootcdn.net/ajax/libs/echarts/5.4.3/echarts.min.js',
    'https://unpkg.com/echarts@5/dist/echarts.min.js',
    'https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js',
]

print(f"开始下载 ECharts 到: {target_file}")
print("-" * 50)

for url in cdn_urls:
    try:
        print(f"尝试从 {url} 下载...")
        urllib.request.urlretrieve(url, str(target_file))
        
        # 检查文件大小
        file_size = os.path.getsize(target_file)
        if file_size > 100000:  # 文件应该大于100KB
            print(f"✓ 下载成功！文件大小: {file_size / 1024:.2f} KB")
            print(f"✓ 文件已保存到: {target_file}")
            print("\n现在请修改 templates/novel/dashboard.html 第129行为:")
            print('  <script src="{% static \'js/echarts.min.js\' %}"></script>')
            break
        else:
            print(f"✗ 文件太小，可能下载失败，尝试下一个CDN...")
            os.remove(target_file)
    except Exception as e:
        print(f"✗ 下载失败: {e}")
        print("尝试下一个CDN...")
        continue
else:
    print("\n所有CDN都无法访问，请手动下载:")
    print("1. 在浏览器访问: https://cdn.bootcdn.net/ajax/libs/echarts/5.4.3/echarts.min.js")
    print("2. 按 Ctrl+S 保存为 echarts.min.js")
    print(f"3. 放到目录: {target_file.parent}")







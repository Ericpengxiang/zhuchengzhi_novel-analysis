"""
前端页面视图
使用Django模板系统渲染HTML页面
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def index(request):
    """首页（预览页面）"""
    return render(request, 'novel/index.html')


@login_required(login_url='/login/')
def dashboard(request):
    """仪表盘"""
    return render(request, 'novel/dashboard.html')


@login_required(login_url='/login/')
def profile(request):
    """个人信息"""
    return render(request, 'novel/profile.html')


@login_required(login_url='/login/')
def favorites(request):
    """用户收藏"""
    return render(request, 'novel/favorites.html')


@login_required(login_url='/login/')
def data_overview(request):
    """数据浏览"""
    # 前端通过API获取数据，这里只返回模板
    return render(request, 'novel/data-overview.html')


@login_required(login_url='/login/')
def type_analysis_1(request):
    """类型分析1"""
    return render(request, 'novel/type-analysis-1.html')


@login_required(login_url='/login/')
def type_analysis_2(request):
    """类型分析2"""
    return render(request, 'novel/type-analysis-2.html')


@login_required(login_url='/login/')
def novel_analysis(request):
    """小说分析"""
    return render(request, 'novel/novel-analysis.html')


@login_required(login_url='/login/')
def user_analysis(request):
    """用户分析"""
    return render(request, 'novel/user-analysis.html')


@login_required(login_url='/login/')
def time_analysis(request):
    """时间分析"""
    return render(request, 'novel/time-analysis.html')


@login_required(login_url='/login/')
def wordcloud(request):
    """词云图"""
    return render(request, 'novel/wordcloud.html')


@login_required(login_url='/login/')
def recommend(request):
    """推荐"""
    return render(request, 'novel/recommend.html')


def login(request):
    """登录页"""
    return render(request, 'novel/login.html')


def register(request):
    """注册页"""
    return render(request, 'novel/register.html')


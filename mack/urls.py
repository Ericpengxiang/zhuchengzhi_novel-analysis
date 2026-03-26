"""
URL configuration for mack project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from novel import views_frontend

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/novel/', include('novel.urls')),  # 小说API接口
    
    # 前端页面路由
    path('', views_frontend.index, name='index'),
    path('dashboard/', views_frontend.dashboard, name='dashboard'),
    path('profile/', views_frontend.profile, name='profile'),
    path('favorites/', views_frontend.favorites, name='favorites'),
    path('data-overview/', views_frontend.data_overview, name='data_overview'),
    path('type-analysis-1/', views_frontend.type_analysis_1, name='type_analysis_1'),
    path('type-analysis-2/', views_frontend.type_analysis_2, name='type_analysis_2'),
    path('novel-analysis/', views_frontend.novel_analysis, name='novel_analysis'),
    path('user-analysis/', views_frontend.user_analysis, name='user_analysis'),
    path('time-analysis/', views_frontend.time_analysis, name='time_analysis'),
    path('wordcloud/', views_frontend.wordcloud, name='wordcloud'),
    path('recommend/', views_frontend.recommend, name='recommend'),
    path('login/', views_frontend.login, name='login'),
    path('register/', views_frontend.register, name='register'),
]

# 开发环境静态文件服务
if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()

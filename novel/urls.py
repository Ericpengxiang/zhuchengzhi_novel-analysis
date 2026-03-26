"""
小说应用URL配置
"""

from django.urls import path
from . import views
from . import views_auth

app_name = 'novel'

urlpatterns = [
    # 用户认证API
    path('auth/register/', views_auth.user_register, name='user_register'),
    path('auth/login/', views_auth.user_login, name='user_login'),
    path('auth/logout/', views_auth.user_logout, name='user_logout'),
    path('auth/info/', views_auth.user_info, name='user_info'),
    path('auth/update/', views_auth.user_update, name='user_update'),
    
    # 基础API
    path('list/', views.novel_list, name='novel_list'),
    path('categories/', views.novel_categories, name='novel_categories'),
    path('detail/<str:book_id>/', views.novel_detail, name='novel_detail'),
    path('chapters/<str:book_id>/', views.novel_chapters, name='novel_chapters'),
    
    # 数据分析API
    path('dashboard/', views.dashboard_stats, name='dashboard_stats'),
    path('data-overview/', views.data_overview_table, name='data_overview'),
    path('type-analysis/', views.type_analysis, name='type_analysis'),
    path('novel-analysis/', views.novel_analysis, name='novel_analysis'),
    path('user-analysis/', views.user_analysis, name='user_analysis'),
    path('time-analysis/', views.time_analysis, name='time_analysis'),
    path('wordcloud/', views.wordcloud_data, name='wordcloud'),
    path('recommend/', views.recommend_novels, name='recommend'),
    path('favorites/', views.favorites_list, name='favorites'),
]


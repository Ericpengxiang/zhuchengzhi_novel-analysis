"""
Django管理命令：检查数据库中的数据
使用方法：python manage.py check_database
"""
from django.core.management.base import BaseCommand
from novel.models import NovelList, NovelDetail, NovelChapter
from django.db import connection


class Command(BaseCommand):
    help = '检查数据库中的数据情况'

    def handle(self, *args, **options):
        cursor = connection.cursor()
        
        print(f"\n{'='*60}")
        print(f"📊 数据库检查")
        print(f"{'='*60}")
        
        # 检查表是否存在
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME IN ('novel_list', 'novel_detail', 'novel_chapters')
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"\n✅ 存在的表: {', '.join(tables) if tables else '无'}")
        
        # 检查novel_detail表结构
        if 'novel_detail' in tables:
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, COLUMN_TYPE, COLUMN_COMMENT
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'novel_detail'
                ORDER BY ORDINAL_POSITION
            """)
            columns = cursor.fetchall()
            print(f"\n📋 novel_detail 表字段 ({len(columns)} 个):")
            for col in columns:
                print(f"   - {col[0]}: {col[2]} ({col[3] or '无注释'})")
        
        # 检查数据量
        print(f"\n📊 数据统计:")
        try:
            novel_list_count = NovelList.objects.count()
            print(f"   novel_list: {novel_list_count} 条")
        except Exception as e:
            print(f"   novel_list: 查询失败 - {e}")
        
        try:
            novel_detail_count = NovelDetail.objects.count()
            print(f"   novel_detail: {novel_detail_count} 条")
        except Exception as e:
            print(f"   novel_detail: 查询失败 - {e}")
        
        try:
            novel_chapters_count = NovelChapter.objects.count()
            print(f"   novel_chapters: {novel_chapters_count} 条")
        except Exception as e:
            print(f"   novel_chapters: 查询失败 - {e}")
        
        # 如果有数据，显示前几条
        if NovelDetail.objects.exists():
            print(f"\n📖 novel_detail 前3条数据:")
            for idx, detail in enumerate(NovelDetail.objects.all()[:3], start=1):
                print(f"\n   [{idx}] {detail.title}")
                print(f"       ID: {detail.book_id}")
                print(f"       作者: {detail.author}")
                print(f"       分类: {detail.category}")
                print(f"       总阅读: {detail.total_read:,}")
                print(f"       评分: {detail.score}")
                # 检查新字段是否存在
                new_fields = [
                    'cover_url', 'author_works_count', 'author_total_words',
                    'continuous_days', 'urge_tickets', 'reward', 
                    'monthly_tickets', 'share_count', 'favorites'
                ]
                for field in new_fields:
                    if hasattr(detail, field):
                        value = getattr(detail, field)
                        print(f"       {field}: {value}")
        
        cursor.close()
        print(f"\n{'='*60}\n")



"""
Django管理命令：从数据库的novel_list表读取数据，采集详情页并保存到novel_detail表
使用方法：python manage.py crawl_details_from_db
"""
import sys
import os

# 添加采集脚本目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../小数采集'))

from django.core.management.base import BaseCommand
from novel.models import NovelList
from django.db import connection


class Command(BaseCommand):
    help = '从数据库novel_list表读取数据，采集详情页并保存到novel_detail表'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='限制采集数量（默认10条，用于测试）',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='采集所有数据（忽略limit限制）',
        )

    def handle(self, *args, **options):
        try:
            # 导入采集脚本的函数
            from faloo_spider import fetch_html, parse_detail
            from mysql_utils import init_database, save_novel_detail, save_novel_chapters
            from dataclasses import asdict
            import time
        except ImportError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ 导入失败: {e}')
            )
            self.stdout.write(
                self.style.ERROR('请确保采集脚本目录存在且可以导入')
            )
            return

        # 获取要采集的小说列表
        if options['all']:
            novels = NovelList.objects.all()
        else:
            novels = NovelList.objects.all()[:options['limit']]

        total_count = novels.count()
        if total_count == 0:
            self.stdout.write(
                self.style.WARNING('⚠️ novel_list 表中没有数据！')
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f'\n📊 开始采集详情页数据')
        )
        self.stdout.write(f'总共需要采集: {total_count} 条')
        self.stdout.write(f"{'='*60}\n")

        all_details = []
        all_chapters = []
        success_count = 0
        fail_count = 0

        for idx, novel in enumerate(novels, start=1):
            self.stdout.write(f"[{idx}/{total_count}] 抓取详情页：{novel.book_url}")
            self.stdout.write(f"    小说: {novel.title}")
            
            try:
                # 采集详情页
                html = fetch_html(novel.book_url)
                detail, chapters = parse_detail(
                    html, 
                    novel.book_url, 
                    cover_url=novel.cover_url
                )
                
                all_details.append(detail)
                all_chapters.extend(chapters)
                success_count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(f"  ✅ 采集成功！")
                )
                self.stdout.write(f"     总阅读: {detail.total_read:,}, 评分: {detail.score}")
                
            except Exception as e:
                fail_count += 1
                self.stdout.write(
                    self.style.ERROR(f"  ❌ 抓取失败：{e}")
                )
                continue
            
            # 每10条保存一次
            if idx % 10 == 0:
                self._save_to_db(all_details, all_chapters)
                self.stdout.write(f"\n💾 已保存 {idx} 条数据到数据库\n")
                all_details = []
                all_chapters = []
            
            time.sleep(1.2)  # 限速

        # 保存剩余数据
        if all_details:
            self._save_to_db(all_details, all_chapters)

        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(
            self.style.SUCCESS(f'✅ 采集完成！')
        )
        self.stdout.write(f"成功: {success_count} 条")
        self.stdout.write(f"失败: {fail_count} 条")
        self.stdout.write(f"{'='*60}\n")

    def _save_to_db(self, all_details, all_chapters):
        """保存数据到数据库"""
        try:
            from mysql_utils import init_database, save_novel_detail, save_novel_chapters
            from dataclasses import asdict
            
            init_database('novel_analysis')
            
            if all_details:
                details_dict = [asdict(d) for d in all_details]
                save_novel_detail(details_dict, db_name='novel_analysis', replace=True)
            
            if all_chapters:
                chapters_dict = [asdict(c) for c in all_chapters]
                save_novel_chapters(chapters_dict, db_name='novel_analysis', replace=True)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'保存到数据库失败：{e}')
            )



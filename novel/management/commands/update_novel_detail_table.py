"""
Django管理命令：更新novel_detail表结构，添加新字段
使用方法：python manage.py update_novel_detail_table
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = '更新novel_detail表结构，添加新字段'

    def handle(self, *args, **options):
        cursor = connection.cursor()
        
        # 需要添加的字段列表
        fields_to_add = [
            ("cover_url", "VARCHAR(500) DEFAULT '' COMMENT '封面图片URL'"),
            ("author_avatar", "VARCHAR(500) DEFAULT '' COMMENT '作者头像URL'"),
            ("author_url", "VARCHAR(500) DEFAULT '' COMMENT '作者页面URL'"),
            ("author_works_count", "INT DEFAULT 0 COMMENT '作品数'"),
            ("author_total_words", "INT DEFAULT 0 COMMENT '创作字数'"),
            ("continuous_days", "INT DEFAULT 0 COMMENT '连更天数'"),
            ("urge_tickets", "INT DEFAULT 0 COMMENT '催更票'"),
            ("reward", "DECIMAL(10,2) DEFAULT 0.0 COMMENT '打赏（元）'"),
            ("monthly_tickets", "INT DEFAULT 0 COMMENT '月票'"),
            ("share_count", "INT DEFAULT 0 COMMENT '分享人数'"),
            ("favorites", "INT DEFAULT 0 COMMENT '收藏数'"),
        ]
        
        added_count = 0
        skipped_count = 0
        
        for field_name, field_def in fields_to_add:
            try:
                # 检查字段是否已存在
                cursor.execute(f"""
                    SELECT COUNT(*) 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = 'novel_detail' 
                    AND COLUMN_NAME = '{field_name}'
                """)
                exists = cursor.fetchone()[0] > 0
                
                if not exists:
                    # 添加字段
                    sql = f"ALTER TABLE `novel_detail` ADD COLUMN `{field_name}` {field_def}"
                    cursor.execute(sql)
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ 成功添加字段: {field_name}')
                    )
                    added_count += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⏭️  字段已存在，跳过: {field_name}')
                    )
                    skipped_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ 添加字段 {field_name} 失败: {e}')
                )
        
        connection.commit()
        cursor.close()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n完成！添加了 {added_count} 个字段，跳过了 {skipped_count} 个已存在的字段。'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                '现在可以重新运行采集脚本来保存新字段的数据了！'
            )
        )



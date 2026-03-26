"""
小说数据模型
对应MySQL数据库中的 novel_list、novel_detail、novel_chapters 表
"""

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """自定义用户模型"""
    nickname = models.CharField(max_length=50, blank=True, default='', verbose_name='昵称')
    avatar = models.CharField(max_length=500, blank=True, default='', verbose_name='头像URL')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'novel_user'
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return self.username


class NovelList(models.Model):
    """小说列表表"""
    book_id = models.CharField(max_length=20, unique=True, db_index=True, verbose_name='小说ID')
    title = models.CharField(max_length=255, verbose_name='标题')
    author = models.CharField(max_length=100, blank=True, default='', verbose_name='作者')
    category = models.CharField(max_length=50, blank=True, default='', db_index=True, verbose_name='分类')
    week_click = models.IntegerField(default=0, db_index=True, verbose_name='周点击')
    word_count = models.CharField(max_length=50, blank=True, default='', verbose_name='字数')
    date_label = models.CharField(max_length=50, blank=True, default='', verbose_name='日期标签')
    intro = models.TextField(blank=True, default='', verbose_name='简介')
    latest_chapter = models.CharField(max_length=255, blank=True, default='', verbose_name='最新章节标题')
    book_url = models.CharField(max_length=500, blank=True, default='', verbose_name='小说详情页链接')
    latest_url = models.CharField(max_length=500, blank=True, default='', verbose_name='最新章节链接')
    cover_url = models.CharField(max_length=500, blank=True, default='', verbose_name='封面图片URL')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'novel_list'
        verbose_name = '小说列表'
        verbose_name_plural = '小说列表'
        ordering = ['-week_click']

    def __str__(self):
        return self.title


class NovelDetail(models.Model):
    """小说详情表"""
    book_id = models.CharField(max_length=20, unique=True, db_index=True, verbose_name='小说ID')
    title = models.CharField(max_length=255, verbose_name='标题')
    author = models.CharField(max_length=100, blank=True, default='', verbose_name='作者')
    category = models.CharField(max_length=50, blank=True, default='', db_index=True, verbose_name='分类')
    sub_category = models.CharField(max_length=50, blank=True, default='', verbose_name='子分类')
    tags = models.CharField(max_length=255, blank=True, default='', verbose_name='标签')
    intro = models.TextField(blank=True, default='', verbose_name='简介')
    month_read = models.IntegerField(default=0, verbose_name='月阅读数')
    month_flower = models.IntegerField(default=0, verbose_name='月鲜花数')
    total_read = models.IntegerField(default=0, verbose_name='总阅读数')
    total_flower = models.IntegerField(default=0, verbose_name='总鲜花数')
    score = models.DecimalField(max_digits=3, decimal_places=1, default=0.0, db_index=True, verbose_name='评分')
    score_count = models.IntegerField(default=0, verbose_name='评分人数')
    in_time = models.CharField(max_length=50, blank=True, default='', verbose_name='入站时间')
    update_time = models.CharField(max_length=50, blank=True, default='', verbose_name='更新时间')
    total_words = models.IntegerField(default=0, verbose_name='总字数')
    read_url = models.CharField(max_length=500, blank=True, default='', verbose_name='阅读链接')
    # 新增字段
    cover_url = models.CharField(max_length=500, blank=True, default='', verbose_name='封面图片URL')
    author_avatar = models.CharField(max_length=500, blank=True, default='', verbose_name='作者头像URL')
    author_url = models.CharField(max_length=500, blank=True, default='', verbose_name='作者页面URL')
    author_works_count = models.IntegerField(default=0, verbose_name='作品数')
    author_total_words = models.IntegerField(default=0, verbose_name='创作字数')
    continuous_days = models.IntegerField(default=0, verbose_name='连更天数')
    urge_tickets = models.IntegerField(default=0, verbose_name='催更票')
    reward = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name='打赏（元）')
    monthly_tickets = models.IntegerField(default=0, verbose_name='月票')
    share_count = models.IntegerField(default=0, verbose_name='分享人数')
    favorites = models.IntegerField(default=0, verbose_name='收藏数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'novel_detail'
        verbose_name = '小说详情'
        verbose_name_plural = '小说详情'
        ordering = ['-score']

    def __str__(self):
        return self.title


class NovelChapter(models.Model):
    """章节表"""
    book_id = models.CharField(max_length=20, db_index=True, verbose_name='小说ID')
    chapter_title = models.CharField(max_length=255, verbose_name='章节标题')
    chapter_url = models.CharField(max_length=500, blank=True, default='', verbose_name='章节链接')
    is_vip = models.SmallIntegerField(default=0, verbose_name='是否VIP（0免费，1VIP）')
    chapter_order = models.IntegerField(default=0, verbose_name='章节顺序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'novel_chapters'
        verbose_name = '章节'
        verbose_name_plural = '章节'
        ordering = ['book_id', 'chapter_order']
        indexes = [
            models.Index(fields=['book_id', 'chapter_order']),
        ]

    def __str__(self):
        return f"{self.book_id} - {self.chapter_title}"


class UserFavorite(models.Model):
    """用户收藏表"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True, verbose_name='用户')
    book_id = models.CharField(max_length=20, db_index=True, verbose_name='小说ID')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')

    class Meta:
        db_table = 'novel_user_favorite'
        verbose_name = '用户收藏'
        verbose_name_plural = '用户收藏'
        unique_together = [['user', 'book_id']]
        indexes = [
            models.Index(fields=['user', 'book_id']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.book_id}"

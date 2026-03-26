from django.contrib import admin
from .models import NovelList, NovelDetail, NovelChapter


@admin.register(NovelList)
class NovelListAdmin(admin.ModelAdmin):
    list_display = ['book_id', 'title', 'author', 'category', 'week_click', 'word_count', 'date_label']
    list_filter = ['category', 'date_label']
    search_fields = ['title', 'author', 'book_id']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(NovelDetail)
class NovelDetailAdmin(admin.ModelAdmin):
    list_display = ['book_id', 'title', 'author', 'category', 'score', 'total_read', 'total_flower']
    list_filter = ['category', 'score']
    search_fields = ['title', 'author', 'book_id']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(NovelChapter)
class NovelChapterAdmin(admin.ModelAdmin):
    list_display = ['book_id', 'chapter_title', 'is_vip', 'chapter_order']
    list_filter = ['is_vip', 'book_id']
    search_fields = ['chapter_title', 'book_id']
    readonly_fields = ['created_at']







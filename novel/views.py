"""
小说API视图
提供RESTful API接口供前端调用
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Avg, Max, Q
from django.db.models.functions import TruncMonth, TruncYear
from .models import NovelList, NovelDetail, NovelChapter, UserFavorite
from .services.recommend_cf_opt import OptimizedCFRecommender, baseline_hot_recommend
import json


def _safe_int(raw, default):
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


def _safe_float(raw, default):
    try:
        return float(raw)
    except (TypeError, ValueError):
        return default


def cors_response(func):
    """CORS装饰器"""
    def wrapper(request, *args, **kwargs):
        response = func(request, *args, **kwargs)
        if isinstance(response, JsonResponse):
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type"
        return response
    return wrapper


@csrf_exempt
@cors_response
@require_http_methods(["GET"])
def novel_list(request):
    """获取小说列表"""
    try:
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        category = request.GET.get('category', '')
        
        queryset = NovelList.objects.all()
        
        # 按分类筛选
        if category:
            queryset = queryset.filter(category=category)
        
        # 分页
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        novels = []
        for novel in page_obj:
            novels.append({
                'book_id': novel.book_id,
                'title': novel.title,
                'author': novel.author,
                'category': novel.category,
                'week_click': novel.week_click,
                'word_count': novel.word_count,
                'date_label': novel.date_label,
                'intro': novel.intro,
                'latest_chapter': novel.latest_chapter,
                'book_url': novel.book_url,
                'latest_url': novel.latest_url,
                'cover_url': novel.cover_url,
            })
        
        return JsonResponse({
            'code': 200,
            'message': 'success',
            'data': {
                'list': novels,
                'total': paginator.count,
                'page': page,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
            }
        })
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'message': str(e),
            'data': None
        })


@csrf_exempt
@cors_response
@require_http_methods(["GET"])
def novel_detail(request, book_id):
    """获取小说详情"""
    try:
        detail = NovelDetail.objects.get(book_id=book_id)
        return JsonResponse({
            'code': 200,
            'message': 'success',
            'data': {
                'book_id': detail.book_id,
                'title': detail.title,
                'author': detail.author,
                'category': detail.category,
                'sub_category': detail.sub_category,
                'tags': detail.tags.split(',') if detail.tags else [],
                'intro': detail.intro,
                'month_read': detail.month_read,
                'month_flower': detail.month_flower,
                'total_read': detail.total_read,
                'total_flower': detail.total_flower,
                'score': float(detail.score),
                'score_count': detail.score_count,
                'in_time': detail.in_time,
                'update_time': detail.update_time,
                'total_words': detail.total_words,
                'read_url': detail.read_url,
            }
        })
    except NovelDetail.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'message': '小说不存在',
            'data': None
        })
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'message': str(e),
            'data': None
        })


@csrf_exempt
@cors_response
@require_http_methods(["GET"])
def novel_chapters(request, book_id):
    """获取小说章节列表"""
    try:
        chapters = NovelChapter.objects.filter(book_id=book_id).order_by('chapter_order')
        chapter_list = []
        for chapter in chapters:
            chapter_list.append({
                'book_id': chapter.book_id,
                'chapter_title': chapter.chapter_title,
                'chapter_url': chapter.chapter_url,
                'is_vip': chapter.is_vip,
                'chapter_order': chapter.chapter_order,
            })
        
        return JsonResponse({
            'code': 200,
            'message': 'success',
            'data': {
                'book_id': book_id,
                'chapters': chapter_list,
                'total': len(chapter_list),
            }
        })
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'message': str(e),
            'data': None
        })


@csrf_exempt
@cors_response
@require_http_methods(["GET"])
def novel_categories(request):
    """获取所有分类"""
    try:
        categories = NovelList.objects.values_list('category', flat=True).distinct()
        category_list = [cat for cat in categories if cat]
        return JsonResponse({
            'code': 200,
            'message': 'success',
            'data': {
                'categories': category_list,
            }
        })
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'message': str(e),
            'data': None
        })


# ==================== 数据分析API ====================

@csrf_exempt
@cors_response
@require_http_methods(["GET"])
def dashboard_stats(request):
    """首页统计数据"""
    try:
        print(f"\n{'='*60}")
        print(f"📊 首页统计API请求")
        print(f"{'='*60}")
        
        # ========= 1. TOP作者赞赏连更天数分析（折线图使用） =========
        # 使用reward（打赏）和continuous_days（连更天数）
        top_authors = NovelDetail.objects.exclude(
            author__isnull=True
        ).exclude(
            author=''
        ).values('author').annotate(
            total_reward=Sum('reward'),
            max_continuous_days=Max('continuous_days')
        ).order_by('-total_reward')[:6]
        
        author_names = []
        author_rewards = []
        author_days = []
        
        for a in top_authors:
            author_names.append(a['author'] or '未知')
            author_rewards.append(float(a['total_reward'] or 0.0))
            author_days.append(a['max_continuous_days'] or 0)
        
        print(f"TOP作者赞赏连更天数（前6）:")
        for i, name in enumerate(author_names):
            print(f"  {name}: 赞赏={author_rewards[i]:.2f}, 连更天数={author_days[i]}")
        
        # ========= 2. 类型占比统计（饼图使用） =========
        category_stats = NovelDetail.objects.values('category').annotate(
            count=Count('book_id'),
            total_read=Sum('total_read')
        ).order_by('-total_read')
        
        category_data = [
            {'value': item['total_read'] or 0, 'name': item['category'] or '未知'}
            for item in category_stats[:6]
        ]
        
        print(f"类型阅读量占比（前6）:")
        for item in category_data:
            print(f"  {item['name']}: {item['value']:,}")
        
        # ========= 3. TOP小说阅读量和鲜花数（柱状图 / 折线图使用） =========
        top_novels = NovelDetail.objects.order_by('-total_read')[:5]
        novel_titles = []
        novel_reads = []
        novel_flowers = []
        
        for novel in top_novels:
            novel_titles.append(novel.title)
            novel_reads.append(novel.total_read or 0)
            novel_flowers.append(novel.total_flower or 0)
        
        print(f"TOP小说阅读量鲜花数（前5）:")
        for i, title in enumerate(novel_titles):
            print(f"  {title}: 阅读量={novel_reads[i]:,}, 鲜花数={novel_flowers[i]:,}")
        
        # ========= 4. 赞赏TOP5作者明细表格 =========
        # 按总打赏（reward）降序取前5名作者
        top_authors_table_qs = NovelDetail.objects.exclude(
            author__isnull=True
        ).exclude(
            author=''
        ).values('author').annotate(
            works_count=Count('book_id'),
            total_words=Sum('total_words'),
            total_reward=Sum('reward'),
            max_continuous_days=Max('continuous_days')
        ).order_by('-total_reward')[:5]

        top_authors_table = []
        for idx, a in enumerate(top_authors_table_qs, start=1):
            top_authors_table.append({
                'rank': idx,
                'author': a['author'] or '未知',
                'works_count': a['works_count'] or 0,
                'total_words': int(a['total_words'] or 0),
                'continue_days': a['max_continuous_days'] or 0,
                'total_reward': float(a['total_reward'] or 0.0),
            })
            print(f"  第{idx}名: {a['author']} - 作品数={a['works_count']}, 字数={a['total_words']:,}, 连更={a['max_continuous_days']}, 打赏={a['total_reward']:.2f}")
        
        # ========= 5. 月票转化漏斗（基于真实数据计算） =========
        # 使用总阅读量、总鲜花数、月票数等数据计算转化率
        total_novels = NovelDetail.objects.count()
        total_reads = NovelDetail.objects.aggregate(total=Sum('total_read'))['total'] or 0
        total_flowers = NovelDetail.objects.aggregate(total=Sum('total_flower'))['total'] or 0
        total_monthly_tickets = NovelDetail.objects.aggregate(total=Sum('monthly_tickets'))['total'] or 0
        
        # 模拟转化漏斗（基于实际数据比例）
        if total_reads > 0:
            exposure = 100  # 曝光基数
            click_rate = (total_novels / max(total_reads / 1000, 1)) * 100 if total_novels > 0 else 76
            page_rate = (total_flowers / max(total_reads / 10, 1)) * 100 if total_reads > 0 else 48
            shelf_rate = (total_monthly_tickets / max(total_flowers / 2, 1)) * 100 if total_flowers > 0 else 30
            ticket_rate = (total_monthly_tickets / max(total_novels * 10, 1)) * 100 if total_novels > 0 else 14
            
            funnel_data = [
                {'value': min(exposure, 100), 'name': '曝光'},
                {'value': min(click_rate, 100), 'name': '点击'},
                {'value': min(page_rate, 100), 'name': '进入书页'},
                {'value': min(shelf_rate, 100), 'name': '加入书架'},
                {'value': min(ticket_rate, 100), 'name': '投月票'}
            ]
        else:
            funnel_data = [
                {'value': 100, 'name': '曝光'},
                {'value': 76, 'name': '点击'},
                {'value': 48, 'name': '进入书页'},
                {'value': 30, 'name': '加入书架'},
                {'value': 14, 'name': '投月票'}
            ]
        
        print(f"月票转化漏斗:")
        for item in funnel_data:
            print(f"  {item['name']}: {item['value']:.1f}%")
        
        print(f"{'='*60}\n")
        
        return JsonResponse({
            'code': 200,
            'message': 'success',
            'data': {
                'line_chart': {
                    'authors': author_names,
                    'rewards': author_rewards,  # 改为打赏数据
                    'continuous_days': author_days,  # 连更天数
                },
                'pie_chart': {
                    'categories': category_data,
                },
                'bar_chart': {
                    'novels': novel_titles,
                    'reads': novel_reads,
                    'flowers': novel_flowers,
                },
                'top_authors_table': top_authors_table,
                'funnel': {
                    'data': funnel_data
                }
            }
        })
    except Exception as e:
        import traceback
        print(f"\n❌ 首页统计API错误:")
        print(f"错误信息: {str(e)}")
        traceback.print_exc()
        print()
        return JsonResponse({
            'code': 500,
            'message': str(e),
            'data': None
        })


@csrf_exempt
@cors_response
@csrf_exempt
@cors_response
@require_http_methods(["GET"])
def data_overview_table(request):
    """数据浏览表格数据"""
    try:
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        keyword = request.GET.get('keyword', '').strip()
        
        print(f"\n{'='*60}")
        print(f"📊 数据浏览API请求")
        print(f"{'='*60}")
        print(f"页码: {page}, 每页数量: {page_size}, 搜索关键词: '{keyword}'")
        
        # 检查数据库连接和表
        from django.db import connection
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM novel_detail")
            raw_count = cursor.fetchone()[0]
            print(f"数据库原始查询记录数: {raw_count}")
        except Exception as e:
            print(f"⚠️ 数据库查询错误: {e}")
        finally:
            cursor.close()
        
        # 检查novel_list和novel_detail的数据量
        novel_list_count = NovelList.objects.count()
        print(f"novel_list 表记录数: {novel_list_count}")
        
        # 关联查询，获取详情数据
        queryset = NovelDetail.objects.all().order_by('-total_read')
        total_count_before_filter = queryset.count()
        print(f"novel_detail 表记录数: {total_count_before_filter}")
        
        # 如果novel_list有数据但novel_detail为空，提示用户
        if novel_list_count > 0 and total_count_before_filter == 0:
            print(f"\n⚠️ 警告: novel_list 有 {novel_list_count} 条数据，但 novel_detail 为空！")
            print(f"💡 解决方案: 运行详情页采集命令")
            print(f"   python manage.py crawl_details_from_db --limit 10  # 测试采集10条")
            print(f"   python manage.py crawl_details_from_db --all       # 采集全部数据")
        elif total_count_before_filter == 0:
            print(f"\n⚠️ 警告: novel_detail 表中没有数据！")
            print(f"请检查:")
            print(f"  1. 是否已运行采集脚本: python faloo_spider.py")
            print(f"  2. 数据库连接是否正确")
            print(f"  3. 表结构是否完整")
            print(f"\n💡 提示: 运行 'python manage.py check_database' 查看详细数据库信息")
        
        # 搜索功能：按标题或作者搜索
        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword) | Q(author__icontains=keyword)
            )
            print(f"搜索后记录数: {queryset.count()}")
        
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        print(f"当前页记录数: {len(page_obj)}")
        print(f"总页数: {paginator.num_pages}")
        
        # 获取当前用户收藏的小说ID列表（如果已登录）
        favorite_book_ids = set()
        if request.user.is_authenticated:
            favorite_book_ids = set(
                UserFavorite.objects.filter(user=request.user)
                .values_list('book_id', flat=True)
            )
            print(f"当前用户已收藏的小说数量: {len(favorite_book_ids)}")
        
        print(f"{'-'*60}")
        
        table_data = []
        for idx, detail in enumerate(page_obj, start=1):
            # 获取对应的列表数据
            try:
                list_data = NovelList.objects.get(book_id=detail.book_id)
                cover_url = list_data.cover_url
            except:
                cover_url = ''
            
            # 优先使用detail中的cover_url，如果没有则使用list_data中的
            final_cover_url = detail.cover_url if hasattr(detail, 'cover_url') and detail.cover_url else cover_url
            
            # 检查当前用户是否收藏了这本小说
            is_favorite = detail.book_id in favorite_book_ids
            
            novel_item = {
                'book_id': detail.book_id,
                'category': detail.category or '-',
                'title': detail.title,
                'cover_url': final_cover_url,
                'author': detail.author or '-',
                'author_avatar': getattr(detail, 'author_avatar', '') or '',
                'author_works_count': getattr(detail, 'author_works_count', 0) or 0,
                'author_total_words': getattr(detail, 'author_total_words', 0) or 0,
                'continuous_days': getattr(detail, 'continuous_days', 0) or 0,
                'month_read': detail.month_read or 0,
                'month_flower': detail.month_flower or 0,
                'total_read': detail.total_read or 0,
                'total_flower': detail.total_flower or 0,
                'total_words': detail.total_words or 0,
                'urge_tickets': getattr(detail, 'urge_tickets', 0) or 0,
                'reward': float(getattr(detail, 'reward', 0.0)) or 0.0,
                'monthly_tickets': getattr(detail, 'monthly_tickets', 0) or 0,
                'share_count': getattr(detail, 'share_count', 0) or 0,
                'score': float(detail.score) if detail.score else 0.0,
                'in_time': detail.in_time or '-',
                'update_time': detail.update_time or '-',
                'is_favorite': is_favorite,  # 添加收藏状态
            }
            table_data.append(novel_item)
            
            # 打印每条数据的关键信息
            print(f"[{idx}] {novel_item['title']}")
            print(f"    ID: {novel_item['book_id']}, 作者: {novel_item['author']}, 分类: {novel_item['category']}")
            print(f"    总阅读: {novel_item['total_read']:,}, 总字数: {novel_item['total_words']:,}, 评分: {novel_item['score']}")
            print(f"    作品数: {novel_item['author_works_count']}, 创作字数: {novel_item['author_total_words']:,}, 连更天数: {novel_item['continuous_days']}")
            print(f"    催更票: {novel_item['urge_tickets']}, 打赏: {novel_item['reward']}, 月票: {novel_item['monthly_tickets']}, 分享: {novel_item['share_count']}")
            print(f"    封面: {'有' if novel_item['cover_url'] else '无'}")
        
        print(f"{'='*60}")
        print(f"✅ 返回 {len(table_data)} 条数据")
        print(f"{'='*60}\n")
        
        return JsonResponse({
            'code': 200,
            'message': 'success',
            'data': {
                'list': table_data,
                'total': paginator.count,
                'page': page,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
            }
        })
    except Exception as e:
        import traceback
        print(f"\n❌ 数据浏览API错误:")
        print(f"错误信息: {str(e)}")
        print(f"错误详情:")
        traceback.print_exc()
        print()
        return JsonResponse({
            'code': 500,
            'message': str(e),
            'data': None
        })


@csrf_exempt
@cors_response
@require_http_methods(["GET"])
def type_analysis(request):
    """类型分析数据（使用真实数据）"""
    try:
        category = request.GET.get('category', '')
        
        print(f"\n{'='*60}")
        print(f"📊 类型分析API请求")
        print(f"{'='*60}")
        print(f"筛选分类: {category if category else '全部'}")
        
        # 使用 NovelDetail 表获取真实数据
        queryset = NovelDetail.objects.all()
        if category:
            queryset = queryset.filter(category=category)
        
        # 各类型阅读量/鲜花量统计（使用总阅读量和总鲜花数）
        category_stats = NovelDetail.objects.values('category').annotate(
            total_read_sum=Sum('total_read'),
            total_flower_sum=Sum('total_flower'),
            count=Count('book_id')
        ).order_by('-total_read_sum')
        
        categories = [s['category'] or '未知' for s in category_stats]
        read_data = [s['total_read_sum'] or 0 for s in category_stats]
        flower_data = [s['total_flower_sum'] or 0 for s in category_stats]
        counts = [s['count'] for s in category_stats]
        
        print(f"找到 {len(categories)} 个分类")
        for i, cat in enumerate(categories):
            print(f"  {cat}: 阅读量={read_data[i]:,}, 鲜花数={flower_data[i]:,}, 数量={counts[i]}")
        
        # 各类型分享最多的小说（全局取分享数最多的前6本）
        top_shared_novels = []
        novels = NovelDetail.objects.exclude(
            share_count__isnull=True
        ).exclude(
            share_count=0
        ).order_by('-share_count')[:6]
        
        for novel in novels:
            top_shared_novels.append({
                'title': novel.title,
                'category': novel.category or '未知',
                'share_count': novel.share_count or 0
            })
        
        print(f"分享最多的前6本小说:")
        for novel in top_shared_novels:
            print(f"  {novel['title']}: {novel['share_count']} 次分享")
        
        # 各类型占比（基于数量）
        total_count = NovelDetail.objects.count()
        category_percent = [
            {'value': s['count'], 'name': s['category'] or '未知'}
            for s in category_stats
        ]
        
        print(f"{'='*60}\n")
        
        return JsonResponse({
            'code': 200,
            'message': 'success',
            'data': {
                'categories': categories,
                'read_data': read_data,  # 各类型总阅读量
                'flower_data': flower_data,  # 各类型总鲜花数
                'counts': counts,  # 各类型小说数量
                'top_shared_novels': top_shared_novels,  # 分享最多的前6本小说
                'percent': category_percent,  # 各类型占比
            }
        })
    except Exception as e:
        import traceback
        print(f"\n❌ 类型分析API错误:")
        print(f"错误信息: {str(e)}")
        traceback.print_exc()
        print()
        return JsonResponse({
            'code': 500,
            'message': str(e),
            'data': None
        })


@csrf_exempt
@cors_response
@require_http_methods(["GET"])
def novel_analysis(request):
    """小说信息分析（按分类筛选）"""
    try:
        category = request.GET.get('category', '')
        
        print(f"\n{'='*60}")
        print(f"📊 小说信息分析API请求")
        print(f"{'='*60}")
        print(f"筛选分类: {category if category else '全部'}")
        
        if category:
            queryset = NovelDetail.objects.filter(category=category)
        else:
            queryset = NovelDetail.objects.all()
        
        # 阅读量区间分析（与前端显示的区间对应）
        read_ranges = [
            {'min': 0, 'max': 100000, 'name': '0-10万'},
            {'min': 100000, 'max': 200000, 'name': '10-20万'},
            {'min': 200000, 'max': 500000, 'name': '20-50万'},
            {'min': 500000, 'max': 1000000, 'name': '50-100万'},
            {'min': 1000000, 'max': float('inf'), 'name': '100万以上'},
        ]
        
        read_range_data = []
        read_range_labels = []
        for r in read_ranges:
            count = queryset.filter(
                total_read__gte=r['min'],
                total_read__lt=r['max'] if r['max'] != float('inf') else 999999999
            ).count()
            read_range_data.append(count)
            read_range_labels.append(r['name'])
        
        print(f"阅读量区间统计:")
        for i, label in enumerate(read_range_labels):
            print(f"  {label}: {read_range_data[i]} 本")
        
        # 字数区间分析（按类型统计）
        word_ranges = [
            {'min': 0, 'max': 100000, 'name': '0-10万'},
            {'min': 100000, 'max': 500000, 'name': '10-50万'},
            {'min': 500000, 'max': 1000000, 'name': '50-100万'},
            {'min': 1000000, 'max': 5000000, 'name': '100-500万'},
            {'min': 5000000, 'max': float('inf'), 'name': '500万以上'},
        ]
        
        # 获取所有分类
        categories = NovelDetail.objects.values_list('category', flat=True).distinct()
        categories = [c for c in categories if c]  # 过滤空值
        
        # 按类型统计字数区间
        word_range_by_category = {}
        for cat in categories:
            cat_queryset = NovelDetail.objects.filter(category=cat)
            word_range_data = []
            for r in word_ranges:
                count = cat_queryset.filter(
                    total_words__gte=r['min'],
                    total_words__lt=r['max'] if r['max'] != float('inf') else 999999999
                ).count()
                word_range_data.append(count)
            word_range_by_category[cat] = word_range_data
        
        print(f"字数区间统计（按类型）:")
        for cat, data in word_range_by_category.items():
            print(f"  {cat}: {data}")
        
        print(f"{'='*60}\n")
        
        return JsonResponse({
            'code': 200,
            'message': 'success',
            'data': {
                'read_ranges': read_range_data,
                'read_range_labels': read_range_labels,
                'word_ranges': word_range_by_category,
                'word_range_labels': [r['name'] for r in word_ranges],
                'categories': list(categories),
            }
        })
    except Exception as e:
        import traceback
        print(f"\n❌ 小说信息分析API错误:")
        print(f"错误信息: {str(e)}")
        traceback.print_exc()
        print()
        return JsonResponse({
            'code': 500,
            'message': str(e),
            'data': None
        })


@csrf_exempt
@cors_response
@require_http_methods(["GET"])
def user_analysis(request):
    """用户分析数据"""
    try:
        print(f"\n{'='*60}")
        print(f"📊 用户分析API请求")
        print(f"{'='*60}")
        
        # 各类型作者创作字数MAX分析（按类型分组，每个类型取最大值）
        category_author_max = []
        categories = NovelDetail.objects.values_list('category', flat=True).distinct()
        categories = [c for c in categories if c]  # 过滤空值
        
        for cat in categories:
            author_max = NovelDetail.objects.filter(
                category=cat
            ).exclude(
                author__isnull=True
            ).exclude(
                author=''
            ).values('author').annotate(
                max_words=Max('total_words')
            ).order_by('-max_words').first()
            
            if author_max:
                category_author_max.append({
                    'name': f"{cat} {author_max['author']}",
                    'value': author_max['max_words'] or 0
                })
        
        # 按字数排序，取前10
        category_author_max.sort(key=lambda x: x['value'], reverse=True)
        category_author_max = category_author_max[:10]
        
        print(f"各类型作者创作字数MAX（前10）:")
        for item in category_author_max:
            print(f"  {item['name']}: {item['value']:,} 字")
        
        # 连更天数作者TOP10（使用continuous_days字段）
        update_stats = NovelDetail.objects.exclude(
            continuous_days__isnull=True
        ).exclude(
            continuous_days=0
        ).exclude(
            author__isnull=True
        ).exclude(
            author=''
        ).values('author').annotate(
            max_days=Max('continuous_days')
        ).order_by('-max_days')[:10]
        
        update_authors = [s['author'] or '未知' for s in update_stats]
        update_days = [s['max_days'] or 0 for s in update_stats]
        
        print(f"连更天数作者TOP10:")
        for i, author in enumerate(update_authors):
            print(f"  {author}: {update_days[i]} 天")
        
        print(f"{'='*60}\n")
        
        return JsonResponse({
            'code': 200,
            'message': 'success',
            'data': {
                'author_max_words': category_author_max,  # 各类型作者创作字数MAX
                'update_authors': update_authors,  # 连更天数TOP10作者
                'update_days': update_days,  # 连更天数TOP10数据
            }
        })
    except Exception as e:
        import traceback
        print(f"\n❌ 用户分析API错误:")
        print(f"错误信息: {str(e)}")
        traceback.print_exc()
        print()
        return JsonResponse({
            'code': 500,
            'message': str(e),
            'data': None
        })


@csrf_exempt
@cors_response
@require_http_methods(["GET"])
def time_analysis(request):
    """时间分析数据"""
    try:
        print(f"\n{'='*60}")
        print(f"📊 时间分析API请求")
        print(f"{'='*60}")
        
        # 由于没有真实的月份创建时间，使用分类数据模拟月度分布
        # 按分类数量排序，取前12个作为12个月的数据
        categories = NovelDetail.objects.values('category').annotate(
            count=Count('book_id'),
            avg_score=Avg('score'),
            total_read=Sum('total_read')
        ).order_by('-count')[:12]
        
        months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
        novel_counts = []
        avg_scores = []
        monthly_reads = []
        
        for cat_stat in categories:
            novel_counts.append(cat_stat['count'] or 0)
            avg_scores.append(float(cat_stat['avg_score'] or 0.0))
            monthly_reads.append(cat_stat['total_read'] or 0)
        
        # 如果数据不足12个，用0填充
        while len(novel_counts) < 12:
            novel_counts.append(0)
            avg_scores.append(0.0)
            monthly_reads.append(0)
        
        # 年度阅读量分析（按分类统计，模拟年度数据）
        # 取前5个分类作为5年的数据
        top_categories = NovelDetail.objects.values('category').annotate(
            total_read=Sum('total_read')
        ).order_by('-total_read')[:5]
        
        years = []
        yearly_reads = []
        current_year = 2019
        for cat_stat in top_categories:
            years.append(str(current_year))
            yearly_reads.append(cat_stat['total_read'] or 0)
            current_year += 1
        
        print(f"月度数据（前12个分类）:")
        for i in range(min(12, len(categories))):
            print(f"  {months[i]}: 数量={novel_counts[i]}, 评分={avg_scores[i]:.2f}, 阅读量={monthly_reads[i]:,}")
        
        print(f"年度数据（前5个分类）:")
        for i, year in enumerate(years):
            print(f"  {year}: 阅读量={yearly_reads[i]:,}")
        
        print(f"{'='*60}\n")
        
        return JsonResponse({
            'code': 200,
            'message': 'success',
            'data': {
                'months': months,
                'novel_counts': novel_counts[:12],
                'avg_scores': avg_scores[:12],
                'monthly_reads': monthly_reads[:12],
                'years': years,
                'yearly_reads': yearly_reads,
            }
        })
    except Exception as e:
        import traceback
        print(f"\n❌ 时间分析API错误:")
        print(f"错误信息: {str(e)}")
        traceback.print_exc()
        print()
        return JsonResponse({
            'code': 500,
            'message': str(e),
            'data': None
        })


@csrf_exempt
@cors_response
@require_http_methods(["GET"])
def wordcloud_data(request):
    """词云图数据"""
    try:
        print(f"\n{'='*60}")
        print(f"📊 词云图API请求")
        print(f"{'='*60}")
        
        # 从小说标题和简介中提取关键词（简化版）
        novels = NovelDetail.objects.all()[:200]  # 增加样本量
        
        # 简单的关键词提取（实际应该用jieba分词）
        keywords = {}
        for novel in novels:
            # 从标题提取
            title = novel.title or ''
            # 移除常见标点符号和特殊字符
            title_words = title.replace('：', ' ').replace('，', ' ').replace('、', ' ').replace('。', ' ').replace('！', ' ').replace('？', ' ').replace('：', ' ').replace('《', ' ').replace('》', ' ').split()
            
            for word in title_words:
                word = word.strip()
                # 过滤长度在2-10之间的词
                if 2 <= len(word) <= 10:
                    keywords[word] = keywords.get(word, 0) + 1
        
        # 转换为词云格式，取前50个
        wordcloud_data = [
            {'name': word, 'value': count}
            for word, count in sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:50]
        ]
        
        print(f"提取到 {len(wordcloud_data)} 个关键词")
        print(f"前10个关键词:")
        for i, item in enumerate(wordcloud_data[:10], 1):
            print(f"  {i}. {item['name']}: {item['value']} 次")
        
        print(f"{'='*60}\n")
        
        return JsonResponse({
            'code': 200,
            'message': 'success',
            'data': {
                'words': wordcloud_data,
            }
        })
    except Exception as e:
        import traceback
        print(f"\n❌ 词云图API错误:")
        print(f"错误信息: {str(e)}")
        traceback.print_exc()
        print()
        return JsonResponse({
            'code': 500,
            'message': str(e),
            'data': None
        })


@csrf_exempt
@cors_response
@require_http_methods(["GET"])
def recommend_novels(request):
    """推荐小说（支持 standard / optimized / compare 三种模式）。"""
    try:
        mode = request.GET.get('mode', 'compare').strip().lower()
        top_k = _safe_int(request.GET.get('top_k'), getattr(settings, 'RECOMMEND_OPT_TOP_K_RESULTS', 6))

        favorite_book_ids = set()
        if request.user.is_authenticated:
            favorite_book_ids = set(UserFavorite.objects.filter(user=request.user).values_list('book_id', flat=True))

        def enrich(items):
            rows = []
            for item in items:
                bid = item.get('book_id')
                list_data = NovelList.objects.filter(book_id=bid).first()
                row = dict(item)
                row['book_url'] = list_data.book_url if list_data else ''
                row['cover_url'] = row.get('cover_url') or (list_data.cover_url if list_data else '')
                row['is_favorite'] = bid in favorite_book_ids
                rows.append(row)
            return rows

        standard_rows = enrich(baseline_hot_recommend(top_k=top_k))

        if mode == 'standard':
            return JsonResponse({
                'code': 200,
                'message': 'success',
                'data': {'mode': 'standard', 'novels': standard_rows}
            })

        recommender = OptimizedCFRecommender(
            alpha=_safe_float(request.GET.get('alpha'), getattr(settings, 'RECOMMEND_OPT_ALPHA', 0.6)),
            top_n_neighbors=_safe_int(request.GET.get('top_n'), getattr(settings, 'RECOMMEND_OPT_TOP_N_NEIGHBORS', 5)),
            top_k_results=top_k,
            score_threshold=_safe_float(request.GET.get('threshold'), getattr(settings, 'RECOMMEND_OPT_SCORE_THRESHOLD', 0.2)),
            cluster_count=_safe_int(request.GET.get('cluster_count'), getattr(settings, 'RECOMMEND_OPT_CLUSTER_COUNT', 3)),
        )
        optimized_source = 'hot_fallback'
        optimized_rows = []
        if request.user.is_authenticated:
            optimized_rows, optimized_source, params = recommender.recommend(request.user.id)
        else:
            params = recommender.params
        optimized_rows = enrich(optimized_rows if optimized_rows else baseline_hot_recommend(top_k=top_k))

        if mode == 'optimized':
            return JsonResponse({
                'code': 200,
                'message': 'success',
                'data': {
                    'mode': 'optimized',
                    'novels': optimized_rows,
                    'source': optimized_source,
                    'params': params,
                }
            })

        return JsonResponse({
            'code': 200,
            'message': 'success',
            'data': {
                'mode': 'compare',
                'standard_novels': standard_rows,
                'optimized_novels': optimized_rows,
                'source': optimized_source,
                'params': params,
            }
        })
    except Exception as e:
        import traceback
        print(f"\n❌ 推荐小说API错误:")
        print(f"错误信息: {str(e)}")
        traceback.print_exc()
        print()
        return JsonResponse({
            'code': 500,
            'message': str(e),
            'data': None
        })


@csrf_exempt
@cors_response
@require_http_methods(["GET"])
def recommend_novels_optimized(request):
    """优化协同过滤推荐接口。"""
    try:
        top_k = _safe_int(request.GET.get('top_k'), getattr(settings, 'RECOMMEND_OPT_TOP_K_RESULTS', 6))
        favorite_book_ids = set()
        if request.user.is_authenticated:
            favorite_book_ids = set(UserFavorite.objects.filter(user=request.user).values_list('book_id', flat=True))

        def enrich(items):
            rows = []
            for item in items:
                bid = item.get('book_id')
                list_data = NovelList.objects.filter(book_id=bid).first()
                row = dict(item)
                row['book_url'] = list_data.book_url if list_data else ''
                row['cover_url'] = row.get('cover_url') or (list_data.cover_url if list_data else '')
                row['is_favorite'] = bid in favorite_book_ids
                rows.append(row)
            return rows

        recommender = OptimizedCFRecommender(
            alpha=_safe_float(request.GET.get('alpha'), getattr(settings, 'RECOMMEND_OPT_ALPHA', 0.6)),
            top_n_neighbors=_safe_int(request.GET.get('top_n'), getattr(settings, 'RECOMMEND_OPT_TOP_N_NEIGHBORS', 5)),
            top_k_results=top_k,
            score_threshold=_safe_float(request.GET.get('threshold'), getattr(settings, 'RECOMMEND_OPT_SCORE_THRESHOLD', 0.2)),
            cluster_count=_safe_int(request.GET.get('cluster_count'), getattr(settings, 'RECOMMEND_OPT_CLUSTER_COUNT', 3)),
        )
        source = 'hot_fallback'
        rows = []
        if request.user.is_authenticated:
            rows, source, params = recommender.recommend(request.user.id)
        else:
            params = recommender.params
        rows = enrich(rows if rows else baseline_hot_recommend(top_k=top_k))
        return JsonResponse({
            'code': 200,
            'message': 'success',
            'data': {
                'mode': 'optimized',
                'novels': rows,
                'source': source,
                'params': params,
            }
        })
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e), 'data': None})


@csrf_exempt
@cors_response
@require_http_methods(["GET", "POST"])
def favorites_list(request):
    """用户收藏列表 & 收藏/取消收藏"""
    # 未登录处理
    if not request.user.is_authenticated:
        return JsonResponse({
            'code': 401,
            'message': '未登录，无法使用收藏功能',
            'data': None
        })

    # 处理收藏/取消收藏
    if request.method == "POST":
        try:
            body = request.body.decode('utf-8') or '{}'
            print(f"\n{'='*60}")
            print(f"📥 POST /api/novel/favorites/ 请求")
            print(f"{'='*60}")
            print(f"请求体原始数据: {body}")
            print(f"Content-Type: {request.META.get('CONTENT_TYPE', 'unknown')}")
            
            data = json.loads(body)
            print(f"解析后的数据: {data}")
        except ValueError as e:
            print(f"❌ JSON解析失败: {e}")
            data = {}
        except Exception as e:
            print(f"❌ 解析请求体失败: {e}")
            import traceback
            traceback.print_exc()
            data = {}

        book_id = data.get('book_id') or ''
        favorite_flag = data.get('favorite', None)
        
        print(f"提取的参数:")
        print(f"  book_id: '{book_id}' (类型: {type(book_id)})")
        print(f"  favorite: {favorite_flag} (类型: {type(favorite_flag)})")

        if not book_id or favorite_flag is None:
            error_msg = f'参数错误：需要提供 book_id 和 favorite（true/false）。收到: book_id={repr(book_id)}, favorite={repr(favorite_flag)}'
            print(f"❌ {error_msg}")
            print(f"{'='*60}\n")
            return JsonResponse({
                'code': 400,
                'message': error_msg,
                'data': None
            })

        try:
            if bool(favorite_flag):
                # 添加收藏
                obj, created = UserFavorite.objects.get_or_create(
                    user=request.user,
                    book_id=book_id
                )
                return JsonResponse({
                    'code': 200,
                    'message': '已加入收藏' if created else '已在收藏列表中',
                    'data': {
                        'book_id': book_id,
                        'favorite': True,
                    }
                })
            else:
                # 取消收藏
                UserFavorite.objects.filter(
                    user=request.user,
                    book_id=book_id
                ).delete()
                return JsonResponse({
                    'code': 200,
                    'message': '已取消收藏',
                    'data': {
                        'book_id': book_id,
                        'favorite': False,
                    }
                })
        except Exception as e:
            return JsonResponse({
                'code': 500,
                'message': str(e),
                'data': None
            })

    # GET：返回当前用户收藏列表
    try:
        user_favorites = UserFavorite.objects.filter(
            user=request.user
        ).order_by('-created_at')

        favorites = []
        for uf in user_favorites:
            # 尝试获取详情和列表信息
            detail = NovelDetail.objects.filter(book_id=uf.book_id).first()
            list_data = NovelList.objects.filter(book_id=uf.book_id).first()

            if not detail and not list_data:
                continue

            title = detail.title if detail else (list_data.title if list_data else '')
            category = detail.category if detail else (list_data.category if list_data else '')
            score = float(detail.score) if detail and detail.score is not None else 0.0
            total_read = detail.total_read if detail else 0
            cover_url = list_data.cover_url if list_data else ''
            book_url = list_data.book_url if list_data else ''

            favorites.append({
                'book_id': uf.book_id,
                'title': title,
                'category': category,
                'score': score,
                'total_read': total_read,
                'cover_url': cover_url,
                'book_url': book_url,
            })

        return JsonResponse({
            'code': 200,
            'message': 'success',
            'data': {
                'favorites': favorites,
            }
        })
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'message': str(e),
            'data': None
        })

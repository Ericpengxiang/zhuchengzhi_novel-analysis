"""
测试数据初始化命令
用法：python manage.py seed_data
功能：创建测试用户、小说列表数据、小说详情数据、用户收藏数据
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from novel.models import User, NovelList, NovelDetail, UserFavorite
import random


class Command(BaseCommand):
    help = '初始化测试数据（用户 + 小说列表 + 小说详情 + 收藏）'

    # ── 真实小说数据（来源：起点中文网热门榜单）──────────────────────
    NOVELS = [
        {
            'book_id': '1010868264', 'title': '诡秘之主', 'author': '爱潜水的乌贼',
            'category': '奇幻', 'sub_category': '西方奇幻',
            'tags': '克苏鲁,西方奇幻,悬疑,神秘',
            'intro': '克莱恩穿越到了一个蒸汽机与魔法并存、光明与黑暗交织的世界。在这里，他以"愚者"为起点，一步步踏上了成为神明的道路。',
            'week_click': 9823456, 'total_read': 1523000000, 'total_flower': 8920000,
            'month_read': 12300000, 'month_flower': 456000,
            'score': 9.3, 'score_count': 1256000,
            'total_words': 3660000, 'continuous_days': 1200,
            'urge_tickets': 980000, 'reward': 2356800.00,
            'monthly_tickets': 1230000, 'share_count': 456000,
            'favorites': 3200000, 'in_time': '2018-09-05',
            'word_count': '366万字', 'date_label': '2018',
        },
        {
            'book_id': '1010394568', 'title': '牧神记', 'author': '宅猪',
            'category': '玄幻', 'sub_category': '东方玄幻',
            'tags': '东方玄幻,修炼,热血,成长',
            'intro': '残缺的神魔身躯，残缺的神魔精血，残缺的神魔意识，造就了一个残缺的少年。但残缺的少年，却要走出一条完整的大道。',
            'week_click': 7654321, 'total_read': 980000000, 'total_flower': 6540000,
            'month_read': 9800000, 'month_flower': 320000,
            'score': 9.1, 'score_count': 980000,
            'total_words': 5120000, 'continuous_days': 1850,
            'urge_tickets': 760000, 'reward': 1890500.00,
            'monthly_tickets': 980000, 'share_count': 320000,
            'favorites': 2800000, 'in_time': '2016-11-20',
            'word_count': '512万字', 'date_label': '2016',
        },
        {
            'book_id': '1010394569', 'title': '遮天', 'author': '辰东',
            'category': '玄幻', 'sub_category': '东方玄幻',
            'tags': '东方玄幻,热血,争霸,成长',
            'intro': '一块石头，一个少年，一段传奇。少年从太古禁地走出，踏上了一条逆天之路，最终成就无上神话。',
            'week_click': 8234567, 'total_read': 1230000000, 'total_flower': 7650000,
            'month_read': 11200000, 'month_flower': 389000,
            'score': 9.0, 'score_count': 1120000,
            'total_words': 6200000, 'continuous_days': 2100,
            'urge_tickets': 890000, 'reward': 2100000.00,
            'monthly_tickets': 1100000, 'share_count': 398000,
            'favorites': 3100000, 'in_time': '2010-07-13',
            'word_count': '620万字', 'date_label': '2010',
        },
        {
            'book_id': '1010394570', 'title': '斗破苍穹', 'author': '天蚕土豆',
            'category': '玄幻', 'sub_category': '东方玄幻',
            'tags': '东方玄幻,热血,丹药,成长',
            'intro': '这里是斗气大陆，没有魔法，没有斗技，只有斗气。一个天才少年萧炎，从废材到强者，书写了一段传奇。',
            'week_click': 9012345, 'total_read': 1890000000, 'total_flower': 9230000,
            'month_read': 13500000, 'month_flower': 512000,
            'score': 9.2, 'score_count': 1560000,
            'total_words': 4500000, 'continuous_days': 1560,
            'urge_tickets': 1050000, 'reward': 2780000.00,
            'monthly_tickets': 1450000, 'share_count': 512000,
            'favorites': 4200000, 'in_time': '2009-02-16',
            'word_count': '450万字', 'date_label': '2009',
        },
        {
            'book_id': '1010394571', 'title': '完美世界', 'author': '辰东',
            'category': '玄幻', 'sub_category': '东方玄幻',
            'tags': '东方玄幻,热血,修炼,争霸',
            'intro': '一粒尘可填海，一根草斩尽日月星辰，弹指间天翻地覆。小石昊从蛮荒之地走出，踏上了一条问鼎完美的道路。',
            'week_click': 7890123, 'total_read': 1100000000, 'total_flower': 7120000,
            'month_read': 10800000, 'month_flower': 365000,
            'score': 9.1, 'score_count': 1050000,
            'total_words': 5800000, 'continuous_days': 1980,
            'urge_tickets': 820000, 'reward': 1950000.00,
            'monthly_tickets': 1050000, 'share_count': 365000,
            'favorites': 2950000, 'in_time': '2012-08-01',
            'word_count': '580万字', 'date_label': '2012',
        },
        {
            'book_id': '1010394572', 'title': '大奉打更人', 'author': '卖报小郎君',
            'category': '玄幻', 'sub_category': '历史神话',
            'tags': '历史,悬疑,推理,修炼',
            'intro': '许七安，大奉打更人，从一个小小的铜锣，一步步成为了这个时代最耀眼的人物。',
            'week_click': 6543210, 'total_read': 780000000, 'total_flower': 5430000,
            'month_read': 8900000, 'month_flower': 298000,
            'score': 9.0, 'score_count': 890000,
            'total_words': 3900000, 'continuous_days': 980,
            'urge_tickets': 650000, 'reward': 1560000.00,
            'monthly_tickets': 890000, 'share_count': 298000,
            'favorites': 2100000, 'in_time': '2019-04-22',
            'word_count': '390万字', 'date_label': '2019',
        },
        {
            'book_id': '1010394573', 'title': '全职高手', 'author': '蝴蝶蓝',
            'category': '都市', 'sub_category': '竞技',
            'tags': '电竞,游戏,热血,竞技',
            'intro': '网游荣耀中被誉为教科书级别的顶尖高手叶修，因为种种原因遭到俱乐部的驱逐，带着一台旧电脑重回荣耀。',
            'week_click': 8765432, 'total_read': 1350000000, 'total_flower': 8100000,
            'month_read': 12000000, 'month_flower': 430000,
            'score': 9.4, 'score_count': 1380000,
            'total_words': 2800000, 'continuous_days': 1100,
            'urge_tickets': 950000, 'reward': 2450000.00,
            'monthly_tickets': 1280000, 'share_count': 430000,
            'favorites': 3600000, 'in_time': '2011-02-26',
            'word_count': '280万字', 'date_label': '2011',
        },
        {
            'book_id': '1010394574', 'title': '择天记', 'author': '猫腻',
            'category': '玄幻', 'sub_category': '东方玄幻',
            'tags': '东方玄幻,热血,成长,修炼',
            'intro': '陈长生，一个从山间小庙走出的少年，带着一本命书，来到了这个世界的中心——国教学院。',
            'week_click': 5432109, 'total_read': 650000000, 'total_flower': 4320000,
            'month_read': 7600000, 'month_flower': 256000,
            'score': 8.8, 'score_count': 760000,
            'total_words': 2900000, 'continuous_days': 860,
            'urge_tickets': 540000, 'reward': 1230000.00,
            'monthly_tickets': 760000, 'share_count': 256000,
            'favorites': 1800000, 'in_time': '2015-06-10',
            'word_count': '290万字', 'date_label': '2015',
        },
        {
            'book_id': '1010394575', 'title': '雪中悍刀行', 'author': '烽火戏诸侯',
            'category': '仙侠', 'sub_category': '武侠',
            'tags': '武侠,江湖,热血,成长',
            'intro': '北凉世子徐凤年，带着一身傲骨，踏上了一条江湖之路。这条路上，有情有义，有恩有仇。',
            'week_click': 6789012, 'total_read': 820000000, 'total_flower': 5890000,
            'month_read': 9200000, 'month_flower': 312000,
            'score': 9.1, 'score_count': 920000,
            'total_words': 6500000, 'continuous_days': 2200,
            'urge_tickets': 710000, 'reward': 1780000.00,
            'monthly_tickets': 920000, 'share_count': 312000,
            'favorites': 2400000, 'in_time': '2013-01-14',
            'word_count': '650万字', 'date_label': '2013',
        },
        {
            'book_id': '1010394576', 'title': '庆余年', 'author': '猫腻',
            'category': '历史', 'sub_category': '历史传奇',
            'tags': '历史,权谋,穿越,成长',
            'intro': '一个来自现代的年轻人，带着超越时代的知识与见识，在一个类似古代的世界里，书写了一段传奇。',
            'week_click': 7123456, 'total_read': 890000000, 'total_flower': 6230000,
            'month_read': 9800000, 'month_flower': 334000,
            'score': 9.2, 'score_count': 980000,
            'total_words': 3500000, 'continuous_days': 1320,
            'urge_tickets': 780000, 'reward': 1980000.00,
            'monthly_tickets': 980000, 'share_count': 334000,
            'favorites': 2600000, 'in_time': '2007-03-28',
            'word_count': '350万字', 'date_label': '2007',
        },
        {
            'book_id': '1010394577', 'title': '将夜', 'author': '猫腻',
            'category': '玄幻', 'sub_category': '东方玄幻',
            'tags': '东方玄幻,热血,成长,修炼',
            'intro': '宁缺，一个从大河国边境走出的少年，带着一把刀，来到了长安城，踏上了一条不平凡的道路。',
            'week_click': 5678901, 'total_read': 690000000, 'total_flower': 4780000,
            'month_read': 8100000, 'month_flower': 278000,
            'score': 9.0, 'score_count': 810000,
            'total_words': 3200000, 'continuous_days': 1050,
            'urge_tickets': 580000, 'reward': 1450000.00,
            'monthly_tickets': 810000, 'share_count': 278000,
            'favorites': 1950000, 'in_time': '2014-08-18',
            'word_count': '320万字', 'date_label': '2014',
        },
        {
            'book_id': '1010394578', 'title': '我的治愈系游戏', 'author': '肉包不吃肉',
            'category': '都市', 'sub_category': '都市生活',
            'tags': '都市,游戏,轻松,治愈',
            'intro': '一款治愈系游戏，让一个普通的上班族，找到了生活的意义。',
            'week_click': 3456789, 'total_read': 420000000, 'total_flower': 2980000,
            'month_read': 5600000, 'month_flower': 189000,
            'score': 8.6, 'score_count': 560000,
            'total_words': 1800000, 'continuous_days': 650,
            'urge_tickets': 340000, 'reward': 780000.00,
            'monthly_tickets': 560000, 'share_count': 189000,
            'favorites': 1200000, 'in_time': '2020-05-12',
            'word_count': '180万字', 'date_label': '2020',
        },
        {
            'book_id': '1010394579', 'title': '赘婿', 'author': '愤怒的香蕉',
            'category': '都市', 'sub_category': '都市传奇',
            'tags': '都市,穿越,权谋,热血',
            'intro': '宁毅，一个来自现代的商业奇才，穿越到了古代，成为了一个赘婿，却在这个世界掀起了滔天巨浪。',
            'week_click': 6234567, 'total_read': 760000000, 'total_flower': 5340000,
            'month_read': 8900000, 'month_flower': 301000,
            'score': 8.9, 'score_count': 890000,
            'total_words': 7200000, 'continuous_days': 2500,
            'urge_tickets': 670000, 'reward': 1680000.00,
            'monthly_tickets': 890000, 'share_count': 301000,
            'favorites': 2200000, 'in_time': '2011-09-01',
            'word_count': '720万字', 'date_label': '2011',
        },
        {
            'book_id': '1010394580', 'title': '一念永恒', 'author': '耳根',
            'category': '仙侠', 'sub_category': '修真文明',
            'tags': '仙侠,修真,热血,成长',
            'intro': '白小纯，一个普通的少年，因为一个机缘，踏上了修仙之路，一念之间，永恒不灭。',
            'week_click': 5901234, 'total_read': 720000000, 'total_flower': 5120000,
            'month_read': 8500000, 'month_flower': 289000,
            'score': 8.9, 'score_count': 850000,
            'total_words': 2600000, 'continuous_days': 890,
            'urge_tickets': 620000, 'reward': 1560000.00,
            'monthly_tickets': 850000, 'share_count': 289000,
            'favorites': 2050000, 'in_time': '2016-04-07',
            'word_count': '260万字', 'date_label': '2016',
        },
        {
            'book_id': '1010394581', 'title': '长夜余火', 'author': '无罪',
            'category': '科幻', 'sub_category': '末世危机',
            'tags': '末世,科幻,热血,成长',
            'intro': '末世降临，人类文明岌岌可危。一个普通的年轻人，在末世中觉醒了超凡力量，开始了守护人类的旅程。',
            'week_click': 2345678, 'total_read': 290000000, 'total_flower': 2010000,
            'month_read': 3800000, 'month_flower': 128000,
            'score': 8.5, 'score_count': 380000,
            'total_words': 1200000, 'continuous_days': 420,
            'urge_tickets': 230000, 'reward': 520000.00,
            'monthly_tickets': 380000, 'share_count': 128000,
            'favorites': 820000, 'in_time': '2022-01-18',
            'word_count': '120万字', 'date_label': '2022',
        },
        {
            'book_id': '1010394582', 'title': '剑来', 'author': '烽火戏诸侯',
            'category': '仙侠', 'sub_category': '修真文明',
            'tags': '仙侠,剑修,热血,成长',
            'intro': '小镇少年陈平安，在一个充满神仙鬼怪的世界里，凭借一把剑，走出了一条属于自己的道路。',
            'week_click': 7456789, 'total_read': 910000000, 'total_flower': 6450000,
            'month_read': 10500000, 'month_flower': 356000,
            'score': 9.3, 'score_count': 1050000,
            'total_words': 8900000, 'continuous_days': 2800,
            'urge_tickets': 850000, 'reward': 2120000.00,
            'monthly_tickets': 1050000, 'share_count': 356000,
            'favorites': 2750000, 'in_time': '2018-02-01',
            'word_count': '890万字', 'date_label': '2018',
        },
        {
            'book_id': '1010394583', 'title': '从红月开始', 'author': '西湖遇雨',
            'category': '科幻', 'sub_category': '超级科技',
            'tags': '科幻,超能力,都市,成长',
            'intro': '一场红月降临，改变了整个世界。林深，一个普通的大学生，在红月中觉醒了特殊能力，开始了新的旅程。',
            'week_click': 1890123, 'total_read': 230000000, 'total_flower': 1560000,
            'month_read': 3100000, 'month_flower': 105000,
            'score': 8.3, 'score_count': 310000,
            'total_words': 980000, 'continuous_days': 320,
            'urge_tickets': 180000, 'reward': 390000.00,
            'monthly_tickets': 310000, 'share_count': 105000,
            'favorites': 650000, 'in_time': '2023-03-15',
            'word_count': '98万字', 'date_label': '2023',
        },
        {
            'book_id': '1010394584', 'title': '大医凌然', 'author': '志鸟村',
            'category': '都市', 'sub_category': '都市生活',
            'tags': '都市,医学,热血,成长',
            'intro': '凌然，一个天才医生，凭借着超凡的医术和坚定的信念，在医学界书写了一段传奇。',
            'week_click': 4567890, 'total_read': 560000000, 'total_flower': 3890000,
            'month_read': 7200000, 'month_flower': 243000,
            'score': 8.8, 'score_count': 720000,
            'total_words': 4100000, 'continuous_days': 1380,
            'urge_tickets': 460000, 'reward': 1120000.00,
            'monthly_tickets': 720000, 'share_count': 243000,
            'favorites': 1650000, 'in_time': '2018-07-23',
            'word_count': '410万字', 'date_label': '2018',
        },
        {
            'book_id': '1010394585', 'title': '我在精神病院学斩神', 'author': '我乃上上签',
            'category': '奇幻', 'sub_category': '都市异能',
            'tags': '都市,异能,悬疑,克苏鲁',
            'intro': '陆离，一个精神病院的普通护工，却发现这个世界远比他想象的要复杂和危险。',
            'week_click': 3234567, 'total_read': 390000000, 'total_flower': 2780000,
            'month_read': 5200000, 'month_flower': 176000,
            'score': 8.7, 'score_count': 520000,
            'total_words': 2300000, 'continuous_days': 760,
            'urge_tickets': 320000, 'reward': 720000.00,
            'monthly_tickets': 520000, 'share_count': 176000,
            'favorites': 1100000, 'in_time': '2021-08-09',
            'word_count': '230万字', 'date_label': '2021',
        },
        {
            'book_id': '1010394586', 'title': '神医凰后', 'author': '风轻扬',
            'category': '历史', 'sub_category': '古代言情',
            'tags': '古代,言情,医术,宫斗',
            'intro': '她是二十一世纪的顶级神医，一朝穿越，成为了相府废柴嫡女。且看她如何凭借一手神医之术，在古代掀起风云。',
            'week_click': 2890123, 'total_read': 350000000, 'total_flower': 2450000,
            'month_read': 4600000, 'month_flower': 156000,
            'score': 8.5, 'score_count': 460000,
            'total_words': 3100000, 'continuous_days': 980,
            'urge_tickets': 280000, 'reward': 640000.00,
            'monthly_tickets': 460000, 'share_count': 156000,
            'favorites': 980000, 'in_time': '2017-11-30',
            'word_count': '310万字', 'date_label': '2017',
        },
    ]

    # ── 测试用户 ──────────────────────────────────────────────────
    TEST_USERS = [
        {'username': 'admin',    'password': 'admin123',  'nickname': '管理员',    'is_staff': True,  'is_superuser': True},
        {'username': 'test',     'password': 'test123',   'nickname': '测试用户',  'is_staff': False, 'is_superuser': False},
        {'username': 'demo',     'password': 'demo123',   'nickname': '演示账号',  'is_staff': False, 'is_superuser': False},
    ]

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('=== 开始初始化测试数据 ==='))

        # 1. 创建测试用户
        self.stdout.write('▶ 创建测试用户...')
        created_users = []
        for u in self.TEST_USERS:
            user, created = User.objects.get_or_create(
                username=u['username'],
                defaults={
                    'password': make_password(u['password']),
                    'nickname': u['nickname'],
                    'is_staff': u['is_staff'],
                    'is_superuser': u['is_superuser'],
                    'email': f"{u['username']}@example.com",
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✔ 创建用户: {u["username"]} / {u["password"]}'))
            else:
                self.stdout.write(f'  - 用户已存在: {u["username"]}')
            created_users.append(user)

        # 2. 写入小说列表 & 小说详情
        self.stdout.write('▶ 写入小说数据...')
        for n in self.NOVELS:
            # novel_list
            NovelList.objects.update_or_create(
                book_id=n['book_id'],
                defaults={
                    'title':          n['title'],
                    'author':         n['author'],
                    'category':       n['category'],
                    'week_click':     n['week_click'],
                    'word_count':     n['word_count'],
                    'date_label':     n['date_label'],
                    'intro':          n['intro'],
                    'latest_chapter': f"第{random.randint(800,2000)}章 终章",
                    'book_url':       f"https://www.qidian.com/book/{n['book_id']}.html",
                    'latest_url':     f"https://www.qidian.com/book/{n['book_id']}/latest.html",
                    'cover_url':      '',
                }
            )
            # novel_detail
            NovelDetail.objects.update_or_create(
                book_id=n['book_id'],
                defaults={
                    'title':              n['title'],
                    'author':             n['author'],
                    'category':           n['category'],
                    'sub_category':       n['sub_category'],
                    'tags':               n['tags'],
                    'intro':              n['intro'],
                    'month_read':         n['month_read'],
                    'month_flower':       n['month_flower'],
                    'total_read':         n['total_read'],
                    'total_flower':       n['total_flower'],
                    'score':              n['score'],
                    'score_count':        n['score_count'],
                    'in_time':            n['in_time'],
                    'update_time':        '2025-03-01',
                    'total_words':        n['total_words'],
                    'read_url':           f"https://www.qidian.com/book/{n['book_id']}.html",
                    'continuous_days':    n['continuous_days'],
                    'urge_tickets':       n['urge_tickets'],
                    'reward':             n['reward'],
                    'monthly_tickets':    n['monthly_tickets'],
                    'share_count':        n['share_count'],
                    'favorites':          n['favorites'],
                    'author_works_count': random.randint(2, 8),
                    'author_total_words': n['total_words'] + random.randint(500000, 3000000),
                }
            )
            self.stdout.write(self.style.SUCCESS(f'  ✔ {n["title"]} ({n["author"]})'))

        # 3. 为 test / demo 用户添加收藏
        self.stdout.write('▶ 添加用户收藏...')
        fav_user = created_users[1]  # test 用户
        fav_books = [n['book_id'] for n in self.NOVELS[:8]]
        for bid in fav_books:
            UserFavorite.objects.get_or_create(user=fav_user, book_id=bid)
        self.stdout.write(self.style.SUCCESS(f'  ✔ 为 {fav_user.username} 添加了 {len(fav_books)} 条收藏'))

        demo_user = created_users[2]  # demo 用户
        demo_books = [n['book_id'] for n in self.NOVELS[5:12]]
        for bid in demo_books:
            UserFavorite.objects.get_or_create(user=demo_user, book_id=bid)
        self.stdout.write(self.style.SUCCESS(f'  ✔ 为 {demo_user.username} 添加了 {len(demo_books)} 条收藏'))

        self.stdout.write(self.style.SUCCESS('\n=== 测试数据初始化完成 ==='))
        self.stdout.write(self.style.WARNING('\n测试账号：'))
        for u in self.TEST_USERS:
            role = '管理员' if u['is_staff'] else '普通用户'
            self.stdout.write(f'  用户名: {u["username"]:10s}  密码: {u["password"]:12s}  角色: {role}')

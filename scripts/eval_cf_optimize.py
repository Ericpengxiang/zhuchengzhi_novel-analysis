"""轻量实验脚本：比较原推荐与优化协同过滤推荐。

运行：
python manage.py shell < scripts/eval_cf_optimize.py
"""

from collections import defaultdict

from django.contrib.auth import get_user_model

from novel.models import UserFavorite
from novel.services.recommend_cf_opt import OptimizedCFRecommender, baseline_hot_recommend


def precision_recall_f1(recommended, relevant):
    if not recommended:
        return 0.0, 0.0, 0.0
    rec_set = set(recommended)
    rel_set = set(relevant)
    hit = len(rec_set & rel_set)
    precision = hit / len(rec_set) if rec_set else 0.0
    recall = hit / len(rel_set) if rel_set else 0.0
    f1 = 0.0 if (precision + recall) == 0 else 2 * precision * recall / (precision + recall)
    return precision, recall, f1


User = get_user_model()
users = list(User.objects.all())

fav_map = defaultdict(list)
for row in UserFavorite.objects.values('user_id', 'book_id').order_by('id'):
    fav_map[row['user_id']].append(row['book_id'])

# 保证有可评估用户
candidate_users = [u.id for u in users if len(fav_map.get(u.id, [])) >= 2]
if not candidate_users:
    print('可评估用户不足，请先运行: python manage.py seed_data')
    raise SystemExit(0)

model = OptimizedCFRecommender()

baseline_scores = []
optimized_scores = []

for uid in candidate_users:
    history = fav_map[uid]
    test_item = history[-1]

    base_recs = [x['book_id'] for x in baseline_hot_recommend(top_k=6)]
    opt_recs, source, _ = model.recommend(uid)
    opt_recs = [x['book_id'] for x in opt_recs]

    baseline_scores.append(precision_recall_f1(base_recs, [test_item]))
    optimized_scores.append(precision_recall_f1(opt_recs, [test_item]))


def avg(rows, idx):
    return sum(r[idx] for r in rows) / len(rows) if rows else 0.0

print('=' * 60)
print('协同过滤优化算法尝试版 - 轻量指标对比')
print(f'评估用户数: {len(candidate_users)}')
print('-' * 60)
print('Baseline(原推荐):')
print(f'  Precision={avg(baseline_scores,0):.4f} Recall={avg(baseline_scores,1):.4f} F1={avg(baseline_scores,2):.4f}')
print('Optimized(优化推荐):')
print(f'  Precision={avg(optimized_scores,0):.4f} Recall={avg(optimized_scores,1):.4f} F1={avg(optimized_scores,2):.4f}')
print('-' * 60)
if avg(optimized_scores,2) >= avg(baseline_scores,2):
    print('结论：优化协同过滤在当前测试集上表现不低于原推荐，可作为论文算法尝试支撑。')
else:
    print('结论：当前样本下优化协同过滤仍需调参，可通过 alpha/threshold/cluster_count 继续优化。')
print('=' * 60)

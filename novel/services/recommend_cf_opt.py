"""优化协同过滤推荐服务。

实现要点：
1. 用户-小说行为矩阵构建（基于收藏行为 + 热门小说隐式反馈补全）。
2. 评分/行为相似度计算（余弦相似度）。
3. 用户特征相似度计算（偏好分类、活跃度、字数偏好等）。
4. 相似度融合：final_sim = alpha * rating_sim + (1-alpha) * profile_sim。
5. 轻量 KMeans 聚类，在目标用户簇内寻找最近邻。
6. 最近邻聚合生成推荐。
7. 冷启动兜底（热门小说 / 分类热门小说）。
"""

from __future__ import annotations

from collections import Counter, defaultdict
from math import sqrt
from random import Random
from typing import Dict, List, Tuple

from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from novel.models import NovelDetail, UserFavorite


class OptimizedCFRecommender:
    """面向小说场景的优化协同过滤尝试版。"""

    def __init__(self, alpha=0.6, top_n_neighbors=5, top_k_results=6, score_threshold=0.2, cluster_count=3):
        self.alpha = float(alpha)
        self.top_n_neighbors = int(top_n_neighbors)
        self.top_k_results = int(top_k_results)
        self.score_threshold = float(score_threshold)
        self.cluster_count = max(1, int(cluster_count))

        self.user_model = get_user_model()
        self.users = list(self.user_model.objects.all())
        self.user_ids = [u.id for u in self.users]
        self.user_index = {uid: idx for idx, uid in enumerate(self.user_ids)}

        self.novel_map = {
            n.book_id: n
            for n in NovelDetail.objects.only(
                'book_id', 'title', 'category', 'score', 'total_read', 'cover_url'
            )
        }

        self.favorites_by_user: Dict[int, set] = defaultdict(set)
        for row in UserFavorite.objects.values('user_id', 'book_id'):
            self.favorites_by_user[row['user_id']].add(row['book_id'])

        self.global_hot = [
            n.book_id
            for n in NovelDetail.objects.order_by('-total_read', '-favorites').only('book_id')[:100]
        ]

        self.user_vectors: Dict[int, Dict[str, float]] = self._build_behavior_matrix()
        self.profile_vectors: Dict[int, List[float]] = self._build_profile_vectors()

    def _build_behavior_matrix(self) -> Dict[int, Dict[str, float]]:
        """构建用户-小说隐式评分矩阵。

        隐式评分映射（论文展示口径）：
        - 收藏: 1.0
        - 阅读: 0.7（同类小说偏好近似）
        - 章节阅读: 0.3（按收藏小说的章节活跃度近似）
        - 点击: 0.1（热门曝光近似）
        """
        vectors: Dict[int, Dict[str, float]] = defaultdict(dict)

        # 收藏行为：1.0
        for uid, books in self.favorites_by_user.items():
            for book_id in books:
                vectors[uid][book_id] = max(vectors[uid].get(book_id, 0), 1.0)

        # 利用已收藏小说的分类，补全“阅读 0.7 / 章节阅读 0.3”近似信号
        category_books = defaultdict(list)
        for bid, novel in self.novel_map.items():
            if novel.category:
                category_books[novel.category].append((bid, novel.total_read or 0))
        for cat in category_books:
            category_books[cat].sort(key=lambda x: x[1], reverse=True)

        for uid in self.user_ids:
            user_books = self.favorites_by_user.get(uid, set())
            categories = [
                self.novel_map[bid].category
                for bid in user_books
                if bid in self.novel_map and self.novel_map[bid].category
            ]
            for cat, _ in Counter(categories).most_common(2):
                for bid, _ in category_books.get(cat, [])[:6]:
                    if bid in user_books:
                        continue
                    vectors[uid][bid] = max(vectors[uid].get(bid, 0), 0.7)
                for bid, _ in category_books.get(cat, [])[6:10]:
                    if bid in user_books:
                        continue
                    vectors[uid][bid] = max(vectors[uid].get(bid, 0), 0.3)

        # 点击近似：热门小说前5给 0.1（冷启动/稀疏补全）
        for uid in self.user_ids:
            if not vectors[uid]:
                for book_id in self.global_hot[:5]:
                    vectors[uid][book_id] = 0.1
            else:
                for book_id in self.global_hot[:3]:
                    vectors[uid][book_id] = max(vectors[uid].get(book_id, 0), 0.1)

        return vectors

    def _build_profile_vectors(self) -> Dict[int, List[float]]:
        """构建用户画像向量：分类偏好 + 活跃度 + 字数偏好。"""
        category_top = list(
            NovelDetail.objects.exclude(category='').values_list('category', flat=True).distinct()[:8]
        )
        vectors: Dict[int, List[float]] = {}

        for uid in self.user_ids:
            fav_books = self.favorites_by_user.get(uid, set())
            fav_details = [self.novel_map[b] for b in fav_books if b in self.novel_map]
            if not fav_details:
                vectors[uid] = [0.0 for _ in category_top] + [0.0, 0.0]
                continue

            cat_counter = Counter([d.category or '未知' for d in fav_details])
            total = max(1, len(fav_details))
            cat_ratio = [cat_counter.get(c, 0) / total for c in category_top]

            active_level = min(1.0, len(fav_books) / 10.0)
            avg_words = sum([d.total_words or 0 for d in fav_details]) / total
            word_pref = min(1.0, avg_words / 3_000_000)

            vectors[uid] = cat_ratio + [active_level, word_pref]

        return vectors

    @staticmethod
    def _cosine_sparse(a: Dict[str, float], b: Dict[str, float]) -> float:
        if not a or not b:
            return 0.0
        common = set(a.keys()) & set(b.keys())
        dot = sum(a[k] * b[k] for k in common)
        norm_a = sqrt(sum(v * v for v in a.values()))
        norm_b = sqrt(sum(v * v for v in b.values()))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    @staticmethod
    def _cosine_dense(a: List[float], b: List[float]) -> float:
        if not a or not b:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sqrt(sum(x * x for x in a))
        norm_b = sqrt(sum(y * y for y in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def _kmeans_cluster(self) -> Dict[int, int]:
        """纯 Python 轻量 KMeans，对用户画像聚类。"""
        if not self.user_ids:
            return {}

        vectors = {uid: self.profile_vectors.get(uid, []) for uid in self.user_ids}
        dims = len(next(iter(vectors.values()), []))
        if dims == 0:
            return {uid: 0 for uid in self.user_ids}

        k = min(self.cluster_count, len(self.user_ids))
        rnd = Random(42)
        centroid_ids = self.user_ids[:]
        rnd.shuffle(centroid_ids)
        centroids = [vectors[uid][:] for uid in centroid_ids[:k]]

        assignments = {uid: 0 for uid in self.user_ids}
        for _ in range(8):
            # assign
            for uid in self.user_ids:
                vec = vectors[uid]
                sims = [self._cosine_dense(vec, c) for c in centroids]
                assignments[uid] = max(range(len(sims)), key=lambda i: sims[i]) if sims else 0

            # update
            for idx in range(k):
                members = [vectors[uid] for uid in self.user_ids if assignments[uid] == idx]
                if not members:
                    continue
                centroids[idx] = [sum(col) / len(col) for col in zip(*members)]

        return assignments

    def _neighbor_candidates(self, user_id: int) -> List[int]:
        assignments = self._kmeans_cluster()
        cluster = assignments.get(user_id, 0)
        return [uid for uid in self.user_ids if uid != user_id and assignments.get(uid, 0) == cluster]

    def _hot_fallback(self, user_id: int, limit: int) -> List[str]:
        favorite_books = self.favorites_by_user.get(user_id, set())
        user_categories = [
            self.novel_map[bid].category
            for bid in favorite_books
            if bid in self.novel_map and self.novel_map[bid].category
        ]

        if user_categories:
            top_category = Counter(user_categories).most_common(1)[0][0]
            preferred = [
                n.book_id
                for n in NovelDetail.objects.filter(category=top_category).order_by('-total_read', '-score')[:50]
            ]
        else:
            preferred = self.global_hot

        result = [bid for bid in preferred if bid not in favorite_books][:limit]
        return result

    def recommend(self, user_id: int) -> Tuple[List[dict], str, dict]:
        """输出推荐结果、来源说明和算法参数。"""
        if user_id not in self.user_index:
            return [], 'unknown_user', self.params

        user_vector = self.user_vectors.get(user_id, {})
        if not user_vector or len(self.favorites_by_user.get(user_id, set())) == 0:
            book_ids = self._hot_fallback(user_id, self.top_k_results)
            return self._serialize(book_ids), 'hot_fallback', self.params

        candidates = self._neighbor_candidates(user_id)
        sims = []
        for other_uid in candidates:
            rating_sim = self._cosine_sparse(user_vector, self.user_vectors.get(other_uid, {}))
            profile_sim = self._cosine_dense(
                self.profile_vectors.get(user_id, []),
                self.profile_vectors.get(other_uid, []),
            )
            final_sim = self.alpha * rating_sim + (1 - self.alpha) * profile_sim
            if final_sim >= self.score_threshold:
                sims.append((other_uid, final_sim))

        sims.sort(key=lambda x: x[1], reverse=True)
        neighbors = sims[: self.top_n_neighbors]

        if not neighbors:
            book_ids = self._hot_fallback(user_id, self.top_k_results)
            return self._serialize(book_ids), 'hot_fallback', self.params

        user_fav = self.favorites_by_user.get(user_id, set())
        item_scores: Dict[str, float] = defaultdict(float)

        for nid, sim in neighbors:
            for book_id, score in self.user_vectors.get(nid, {}).items():
                if book_id in user_fav:
                    continue
                item_scores[book_id] += sim * score

        ranked = [bid for bid, _ in sorted(item_scores.items(), key=lambda x: x[1], reverse=True)]
        if len(ranked) < self.top_k_results:
            ranked.extend(self._hot_fallback(user_id, self.top_k_results))

        deduped = []
        for bid in ranked:
            if bid not in deduped and bid not in user_fav:
                deduped.append(bid)
            if len(deduped) >= self.top_k_results:
                break

        return self._serialize(deduped), 'fused_neighbor_cf', self.params

    def _serialize(self, book_ids: List[str]) -> List[dict]:
        data = []
        for bid in book_ids:
            novel = self.novel_map.get(bid)
            if not novel:
                continue
            data.append({
                'book_id': novel.book_id,
                'title': novel.title,
                'category': novel.category or '未知',
                'score': float(novel.score or 0.0),
                'total_read': novel.total_read or 0,
                'cover_url': novel.cover_url or '',
            })
        return data

    @property
    def params(self) -> dict:
        return {
            'alpha': self.alpha,
            'top_n_neighbors': self.top_n_neighbors,
            'top_k_results': self.top_k_results,
            'score_threshold': self.score_threshold,
            'cluster_count': self.cluster_count,
        }



def baseline_hot_recommend(top_k=6) -> List[dict]:
    """原始基线推荐（评分+阅读）。"""
    novels: QuerySet = NovelDetail.objects.filter(score__gte=7.0).order_by('-score', '-total_read')[:top_k]
    return [
        {
            'book_id': n.book_id,
            'title': n.title,
            'category': n.category or '未知',
            'score': float(n.score or 0.0),
            'total_read': n.total_read or 0,
            'cover_url': n.cover_url or '',
        }
        for n in novels
    ]

/**
 * API调用工具
 * 用于前端页面调用Django后端API获取真实数据
 */

const API_BASE_URL = '/api/novel';

/**
 * 通用API请求函数
 */
async function apiRequest(url, options = {}) {
    try {
        // 确保 headers 正确设置
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };
        
        // 构建请求配置
        const fetchOptions = {
            method: options.method || 'GET',
            headers: headers,
            credentials: 'include',
        };
        
        // 如果有 body，添加到配置中
        if (options.body) {
            fetchOptions.body = options.body;
        }
        
        // 合并其他选项（但 body 和 headers 已经处理过了）
        Object.keys(options).forEach(key => {
            if (key !== 'headers' && key !== 'body') {
                fetchOptions[key] = options[key];
            }
        });
        
        console.log('API请求:', url, fetchOptions);
        
        const response = await fetch(url, fetchOptions);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API请求失败:', error);
        return { code: 500, message: error.message, data: null };
    }
}

/**
 * 获取小说列表
 */
async function getNovelList(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return await apiRequest(`${API_BASE_URL}/list/?${queryString}`);
}

/**
 * 获取小说详情
 */
async function getNovelDetail(bookId) {
    return await apiRequest(`${API_BASE_URL}/detail/${bookId}/`);
}

/**
 * 获取章节列表
 */
async function getNovelChapters(bookId) {
    return await apiRequest(`${API_BASE_URL}/chapters/${bookId}/`);
}

/**
 * 获取所有分类
 */
async function getCategories() {
    return await apiRequest(`${API_BASE_URL}/categories/`);
}

/**
 * 获取首页统计数据
 */
async function getDashboardStats() {
    return await apiRequest(`${API_BASE_URL}/dashboard/`);
}

/**
 * 获取数据浏览表格数据
 */
async function getDataOverview(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return await apiRequest(`${API_BASE_URL}/data-overview/?${queryString}`);
}

/**
 * 获取类型分析数据
 */
async function getTypeAnalysis(category = '') {
    const url = category 
        ? `${API_BASE_URL}/type-analysis/?category=${encodeURIComponent(category)}`
        : `${API_BASE_URL}/type-analysis/`;
    return await apiRequest(url);
}

/**
 * 获取小说分析数据
 */
async function getNovelAnalysis(category = '') {
    const url = category 
        ? `${API_BASE_URL}/novel-analysis/?category=${encodeURIComponent(category)}`
        : `${API_BASE_URL}/novel-analysis/`;
    return await apiRequest(url);
}

/**
 * 获取用户分析数据
 */
async function getUserAnalysis() {
    return await apiRequest(`${API_BASE_URL}/user-analysis/`);
}

/**
 * 获取时间分析数据
 */
async function getTimeAnalysis() {
    return await apiRequest(`${API_BASE_URL}/time-analysis/`);
}

/**
 * 获取词云数据
 */
async function getWordcloudData() {
    return await apiRequest(`${API_BASE_URL}/wordcloud/`);
}

/**
 * 获取推荐小说
 */
async function getRecommendNovels() {
    return await apiRequest(`${API_BASE_URL}/recommend/`);
}

/**
 * 获取优化协同过滤推荐
 */
async function getOptimizedRecommendNovels(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return await apiRequest(`${API_BASE_URL}/recommend/optimized/${queryString ? `?${queryString}` : ''}`);
}

/**
 * 获取推荐对比结果（原推荐 vs 优化推荐）
 */
async function getRecommendCompare(params = {}) {
    const merged = { mode: 'compare', ...params };
    const queryString = new URLSearchParams(merged).toString();
    return await apiRequest(`${API_BASE_URL}/recommend/?${queryString}`);
}

/**
 * 获取收藏列表
 */
async function getFavorites() {
    return await apiRequest(`${API_BASE_URL}/favorites/`);
}

/**
 * 设置收藏 / 取消收藏
 * @param {string} bookId 小说ID
 * @param {boolean} favorite true=收藏，false=取消收藏
 */
async function setFavorite(bookId, favorite) {
    // 参数验证
    if (!bookId || bookId === 'null' || bookId === 'undefined') {
        console.error('setFavorite: bookId 无效', bookId);
        return { code: 400, message: '小说ID不能为空', data: null };
    }
    
    if (typeof favorite !== 'boolean') {
        console.error('setFavorite: favorite 必须是布尔值', favorite);
        return { code: 400, message: 'favorite 参数必须是布尔值', data: null };
    }
    
    const requestData = {
        book_id: String(bookId),
        favorite: Boolean(favorite)
    };
    
    console.log('setFavorite 请求数据:', requestData);
    
    return await apiRequest(`${API_BASE_URL}/favorites/`, {
        method: 'POST',
        body: JSON.stringify(requestData),
    });
}



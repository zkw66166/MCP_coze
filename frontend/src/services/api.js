/**
 * API 服务 - 与 FastAPI 后端通信
 */

// API 基础 URL（开发环境使用 Vite 代理，生产环境使用相对路径）
const API_BASE_URL = 'http://localhost:8000';

/**
 * 获取认证请求头
 */
function getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    const headers = {
        'Content-Type': 'application/json',
    };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
}

/**
 * 认证 API - 登录
 */
export async function login(username, password) {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || '登录失败');
    }

    return response.json();
}

/**
 * 认证 API - 登出
 */
export async function logout() {
    const response = await fetch(`${API_BASE_URL}/api/auth/logout`, {
        method: 'POST',
        headers: getAuthHeaders(),
    });

    if (!response.ok) {
        throw new Error('登出失败');
    }

    // 清除本地存储
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');

    return response.json();
}

/**
 * 认证 API - 获取当前用户信息
 */
export async function getCurrentUser() {
    const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
        headers: getAuthHeaders(),
    });

    if (!response.ok) {
        throw new Error('获取用户信息失败');
    }

    return response.json();
}

/**
 * 获取企业列表
 */
export async function fetchCompanies() {
    const response = await fetch(`${API_BASE_URL}/api/companies`, {
        headers: getAuthHeaders(),
    });
    if (!response.ok) {
        throw new Error(`获取企业列表失败: ${response.status}`);
    }
    return response.json();
}

/**
 * 获取统计信息
 */
export async function fetchStatistics() {
    const response = await fetch(`${API_BASE_URL}/api/statistics`);
    if (!response.ok) {
        throw new Error(`获取统计信息失败: ${response.status}`);
    }
    return response.json();
}

/**
 * 流式聊天 API
 * @param {string} question 用户问题
 * @param {number|null} companyId 企业 ID（可选）
 * @param {string} responseMode 回答模式 ('detailed' | 'standard' | 'concise')
 * @param {function} onMessage 收到消息回调
 * @param {function} onRoute 路由事件回调
 * @param {function} onChart 图表数据回调
 * @param {function} onSummary 分析总结回调（新增）
 * @param {function} onError 错误回调
 * @param {function} onDone 完成回调
 * @returns {AbortController} 用于取消请求
 */
export function streamChat(question, companyId, responseMode, { onMessage, onRoute, onChart, onSummary, onError, onDone }) {
    const controller = new AbortController();

    const fetchData = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/chat`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify({
                    question,
                    company_id: companyId,
                    enable_routing: true,
                    // show_chart 由 responseMode 决定 (仅 detailed 模式为 true)
                    show_chart: responseMode === 'detailed',
                    response_mode: responseMode || 'detailed'
                }),
                signal: controller.signal
            });

            if (!response.ok) {
                throw new Error(`API 错误: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            let currentEvent = '';

            while (true) {
                const { done, value } = await reader.read();

                if (done) {
                    break;
                }

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (line.startsWith('event: ')) {
                        currentEvent = line.slice(7).trim();
                        continue;
                    }

                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));

                            // 根据事件类型处理
                            if (currentEvent === 'chart') {
                                onChart?.(data);
                            } else if (currentEvent === 'summary') {
                                // 分析总结（渲染在图表之后）
                                onSummary?.(data.content);
                            } else if (data.content !== undefined) {
                                onMessage?.(data.content);
                            }

                            if (data.path !== undefined) {
                                onRoute?.(data.path, data.company);
                            }

                            if (data.status === 'completed') {
                                onDone?.();
                            }

                            if (data.message !== undefined && currentEvent === 'error') {
                                onError?.(data.message);
                            }
                        } catch (e) {
                            // 忽略解析错误
                        }
                    }
                }
            }

            onDone?.();
        } catch (error) {
            if (error.name !== 'AbortError') {
                onError?.(error.message);
            }
        }
    };

    fetchData();

    return controller;
}

/**
 * 获取企业画像数据
 * @param {number} companyId 企业 ID
 * @param {number|null} year 年份（可选，默认当年）
 */
export async function fetchCompanyProfile(companyId, year = null) {
    let url = `${API_BASE_URL}/api/company-profile/${companyId}`;
    if (year) {
        url += `?year=${year}`;
    }
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`获取企业画像失败: ${response.status}`);
    }
    return response.json();
}

/**
 * 获取企业画像基本信息
 */
export async function fetchProfileBasic(companyId) {
    const response = await fetch(`${API_BASE_URL}/api/company-profile/${companyId}/basic`);
    if (!response.ok) {
        throw new Error(`获取基本信息失败: ${response.status}`);
    }
    return response.json();
}

/**
 * 获取企业股东信息
 */
export async function fetchProfileShareholders(companyId) {
    const response = await fetch(`${API_BASE_URL}/api/company-profile/${companyId}/shareholders`);
    if (!response.ok) {
        throw new Error(`获取股东信息失败: ${response.status}`);
    }
    return response.json();
}

/**
 * 健康检查
 */
export async function healthCheck() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        return response.ok;
    } catch {
        return false;
    }
}

/**
 * 获取数据管理统计信息
 * @param {number|null} companyId 企业 ID (可选，不传则为多户汇总)
 */
export async function fetchDataManagementStats(companyId) {
    let url = `${API_BASE_URL}/api/data-management/stats`;
    if (companyId) {
        url += `?company_id=${companyId}`;
    }
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`获取数据管理统计失败: ${response.status}`);
    }
    return response.json();
}

export async function runDataQualityCheck(companyId) {
    let url = `${API_BASE_URL}/api/data-management/quality-check`;
    if (companyId) {
        url += `?company_id=${companyId}`;
    }
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    });
    if (!response.ok) {
        throw new Error(`执行数据质量检查失败: ${response.status}`);
    }
    return response.json();
}

/**
 * 获取数据浏览支持的企业列表
 */
export async function fetchBrowseCompanies() {
    const response = await fetch(`${API_BASE_URL}/api/data-browser/companies`);
    if (!response.ok) {
        throw new Error(`获取企业列表失败: ${response.status}`);
    }
    return response.json();
}

/**
 * 获取数据浏览支持的表列表
 */
export async function fetchBrowseTables() {
    const response = await fetch(`${API_BASE_URL}/api/data-browser/tables`);
    if (!response.ok) {
        throw new Error(`获取数据表列表失败: ${response.status}`);
    }
    return response.json();
}

/**
 * 获取指定企业和表的数据期间
 */
export async function fetchBrowsePeriods(companyId, tableName) {
    const response = await fetch(`${API_BASE_URL}/api/data-browser/periods?company_id=${companyId}&table_name=${tableName}`);
    if (!response.ok) {
        throw new Error(`获取数据期间失败: ${response.status}`);
    }
    return response.json();
}

/**
 * 获取表数据 (不分页)
 */
export async function fetchBrowseData(companyId, tableName, period = null) {
    let url = `${API_BASE_URL}/api/data-browser/data?company_id=${companyId}&table_name=${tableName}`;
    if (period) {
        url += `&period=${encodeURIComponent(period)}`;
    }
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`获取数据失败: ${response.status}`);
    }
    return response.json();
}

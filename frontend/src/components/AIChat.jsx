import { useState, useEffect, useCallback, useRef } from 'react';
import ChatWidget from './ChatWidget';
import { streamChat } from '../services/api';
import './AIChat.css';

/**
 * AI智问页面组件
 */
function AIChat({ selectedCompanyId, companies }) {
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [history, setHistory] = useState([]);
    const [inputText, setInputText] = useState('');
    const [currentController, setCurrentController] = useState(null);
    const [selectedHistory, setSelectedHistory] = useState(new Set());  // 新增: 选中的历史记录
    const [responseMode, setResponseMode] = useState('detailed'); // 新增: 回答模式 (detailed/standard/concise)
    const [isSelectionMode, setIsSelectionMode] = useState(false); // 新增: 消息选择模式
    const [selectedMessageIndices, setSelectedMessageIndices] = useState(new Set()); // 新增: 选中的消息索引
    const chatWidgetRef = useRef(null);

    const historyListRef = useRef(null); // Ref for history list scrolling
    const historyNavRef = useRef({});    // Ref for history navigation state { [question]: lastIndex }

    // 加载历史记录
    const fetchHistory = useCallback(async () => {
        try {
            const token = localStorage.getItem('access_token');
            const res = await fetch('/api/chat/history?limit=100', {
                headers: {
                    'Authorization': token ? `Bearer ${token}` : ''
                }
            }); // Load last 100 messages
            if (res.ok) {
                const data = await res.json();
                // Convert DB format to UI format
                // DB: { id, role, content, type, created_at }
                // UI: { role, content, ... }
                // Type handling: if type is chart or content contains <CHART_DATA>, parse it.

                const formattedMessages = data.map(msg => {
                    let content = msg.content;
                    let charts = [];
                    let summary = '';

                    // Try to extract chart data from content tag <CHART_DATA>
                    if (content && content.includes('<CHART_DATA>')) {
                        const parts = content.split('<CHART_DATA>');
                        // parts[0] is text before, parts[1] is json, parts[2] is after (if any)
                        // This is a simple parser, might need robustness
                        if (parts.length >= 2) {
                            content = parts[0]; // Text part
                            try {
                                const chartJson = parts[1].split('</CHART_DATA>')[0];
                                charts.push(JSON.parse(chartJson));
                            } catch (e) {
                                console.error('Error parsing chart data', e);
                            }
                            // Check for summary? usually summary is part of text or separate
                        }
                    }

                    // Extract summary from text if marked (from backend standard)
                    if (content && content.includes('**总结**:')) {
                        const sumParts = content.split('**总结**:');
                        if (sumParts.length > 1) {
                            content = sumParts[0];
                            summary = sumParts[1];
                        }
                    }

                    return {
                        id: msg.id, // Keep ID for deletion
                        role: msg.role,
                        content: content,
                        charts: charts.length > 0 ? charts : undefined,
                        summary: summary || undefined,
                        timestamp: new Date(msg.created_at).toLocaleTimeString('zh-CN', { hour12: false })
                    };
                });
                setMessages(formattedMessages);
                console.log('🔵 setMessages called with', formattedMessages.length, 'messages');

                // Derive history list (unique user questions)
                const userQuestions = formattedMessages
                    .filter(m => m.role === 'user')
                    .map(m => m.content)
                    .reverse(); // Newest first
                setHistory([...new Set(userQuestions)]);
            } else {
                console.error('🔴 fetchHistory failed with status:', res.status);
            }
        } catch (error) {
            console.error('Failed to load history:', error);
        }
    }, []);

    useEffect(() => {
        fetchHistory();
    }, [fetchHistory]);

    // 保存历史记录 (No longer needed for LocalStorage, but maybe for state updates?)
    // We rely on backend persistence now.

    // 发送消息
    const handleSend = useCallback(() => {
        const question = inputText.trim();
        if (!question || isLoading) return;

        // 添加用户消息
        const timestamp = new Date().toLocaleTimeString('zh-CN', { hour12: false });
        setMessages(prev => [...prev, { role: 'user', content: question, timestamp }]);
        setMessages(prev => [...prev, { role: 'assistant', content: '', route: null }]);
        setIsLoading(true);
        setInputText('');

        // 保存到历史记录 (Frontend update for immediate UI feedback)
        const filteredHistory = history.filter(h => h !== question);
        const newHistory = [question, ...filteredHistory.slice(0, 49)];
        setHistory(newHistory);
        // saveHistory(newHistory); // Removed LocalStorage

        // 滚动历史记录到顶部
        if (historyListRef.current) {
            setTimeout(() => {
                historyListRef.current.scrollTop = 0;
            }, 0);
        }

        // 流式请求
        const controller = streamChat(question, selectedCompanyId, responseMode, {
            onMessage: (content) => {
                setMessages(prev => {
                    const newMessages = [...prev];
                    const lastIdx = newMessages.length - 1;
                    if (lastIdx >= 0 && newMessages[lastIdx].role === 'assistant') {
                        newMessages[lastIdx] = {
                            ...newMessages[lastIdx],
                            content: newMessages[lastIdx].content + content
                        };
                    }
                    return newMessages;
                });
            },
            onRoute: (route) => {
                setMessages(prev => {
                    const newMessages = [...prev];
                    const lastIdx = newMessages.length - 1;
                    if (lastIdx >= 0 && newMessages[lastIdx].role === 'assistant') {
                        newMessages[lastIdx] = { ...newMessages[lastIdx], route };
                    }
                    return newMessages;
                });
            },
            onChart: (chartData) => {
                setMessages(prev => {
                    const newMessages = [...prev];
                    const lastIdx = newMessages.length - 1;
                    if (lastIdx >= 0 && newMessages[lastIdx].role === 'assistant') {
                        const currentCharts = newMessages[lastIdx].charts || [];
                        newMessages[lastIdx] = {
                            ...newMessages[lastIdx],
                            charts: [...currentCharts, chartData]
                        };
                    }
                    return newMessages;
                });
            },
            onSummary: (content) => {
                // 分析总结（渲染在图表之后）
                setMessages(prev => {
                    const newMessages = [...prev];
                    const lastIdx = newMessages.length - 1;
                    if (lastIdx >= 0 && newMessages[lastIdx].role === 'assistant') {
                        const currentSummary = newMessages[lastIdx].summary || '';
                        newMessages[lastIdx] = {
                            ...newMessages[lastIdx],
                            summary: currentSummary + content
                        };
                    }
                    return newMessages;
                });
            },
            onError: (error) => {
                setMessages(prev => {
                    const newMessages = [...prev];
                    const lastIdx = newMessages.length - 1;
                    if (lastIdx >= 0 && newMessages[lastIdx].role === 'assistant') {
                        newMessages[lastIdx] = {
                            ...newMessages[lastIdx],
                            content: newMessages[lastIdx].content + `\n\n❌ 错误: ${error}`
                        };
                    }
                    return newMessages;
                });
                setIsLoading(false);
            },
            onDone: () => setIsLoading(false)
        });

        setCurrentController(controller);
    }, [inputText, isLoading, selectedCompanyId, history, responseMode]);

    const handleClear = useCallback(async () => {
        if (window.confirm('确定要清空所有对话吗？此操作无法撤销。')) {
            if (currentController) currentController.abort();

            try {
                const token = localStorage.getItem('access_token');
                await fetch('/api/chat/history', {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': token ? `Bearer ${token}` : ''
                    },
                    body: JSON.stringify({ delete_all: true, target: 'chat' })
                });
                setMessages([]);
                // Don't clear sidebar history anymore - they're separate now
                setIsLoading(false);
                setIsSelectionMode(false);
                setSelectedMessageIndices(new Set());
            } catch (e) {
                alert('删除失败');
            }
        }
    }, [currentController]);

    // 切换选择模式
    const toggleSelectionMode = useCallback(() => {
        setIsSelectionMode(prev => !prev);
        setSelectedMessageIndices(new Set()); // 进入或退出都重置选择
    }, []);

    // 切换单条消息选中
    const toggleMessageSelection = useCallback((index) => {
        setSelectedMessageIndices(prev => {
            const newSet = new Set(prev);
            if (newSet.has(index)) {
                newSet.delete(index);
            } else {
                newSet.add(index);
            }
            return newSet;
        });
    }, []);

    // 删除选中的消息
    const handleDeleteSelectedMessages = useCallback(async () => {
        if (selectedMessageIndices.size === 0) return;

        if (window.confirm(`确定删除选中的 ${selectedMessageIndices.size} 条消息吗？`)) {
            // Get IDs of selected messages
            const idsToDelete = [];
            const indices = Array.from(selectedMessageIndices);
            indices.forEach(idx => {
                if (messages[idx] && messages[idx].id) {
                    idsToDelete.push(messages[idx].id);
                }
            });

            if (idsToDelete.length > 0) {
                try {
                    const token = localStorage.getItem('access_token');
                    await fetch('/api/chat/history', {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': token ? `Bearer ${token}` : ''
                        },
                        body: JSON.stringify({ message_ids: idsToDelete, target: 'chat' })
                    });
                } catch (e) {
                    console.error("Delete failed", e);
                }
            }

            setMessages(prev => prev.filter((_, index) => !selectedMessageIndices.has(index)));
            setIsSelectionMode(false); // 删除后退出选择模式
            setSelectedMessageIndices(new Set());

            // Refresh history list? 
            // Ideally we re-fetch or filter locally. 
            // Local filter for history sidebar is hard because it's derived.
            // Let's just re-fetch to be safe or leave it (sidebar history is question based)
            fetchHistory();
        }
    }, [selectedMessageIndices, messages, fetchHistory]);

    // 导出 PDF
    const handleExportPDF = useCallback(async () => {
        if (messages.length === 0) {
            alert('没有对话内容需要导出');
            return;
        }

        // 1. 立即打开窗口，避开浏览器拦截
        const printWindow = window.open('', '_blank');
        if (!printWindow) {
            alert('无法打开打印窗口，请检查是否被浏览器拦截');
            return;
        }

        // 2. 显示加载提示
        printWindow.document.write('<!DOCTYPE html><html><head><title>正在生成...</title></head><body><div style="font-family: sans-serif; padding: 20px; text-align: center;">正在生成对话记录，请稍候...</div></body></html>');

        try {
            const { marked } = await import('marked');
            marked.setOptions({ breaks: true, gfm: true });

            let htmlContent = `<!DOCTYPE html><html><head><meta charset="UTF-8"><title>对话记录</title>
            <style>
                * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
                body { font-family: 'Microsoft YaHei', sans-serif; padding: 15px; line-height: 1.5; font-size: 12px; }
                .user { background: #eff6ff !important; padding: 8px 12px; border-radius: 6px; margin: 8px 0; }
                .assistant { background: #f8fafc !important; border: 1px solid #e5e7eb; padding: 10px 12px; border-radius: 6px; margin: 8px 0; }
                .assistant table { width: 100%; border-collapse: collapse; margin: 8px 0; }
                .assistant th, .assistant td { border: 1px solid #d1d5db !important; padding: 4px 8px; }
                .assistant th { background: #f9fafb !important; }
                .assistant img { max-width: 100%; -webkit-print-color-adjust: exact !important; }
                h1.title { text-align: center; font-size: 18px; }
                @media print { img { max-height: 300px; } }
            </style></head><body>
            <h1 class="title">💬 税务智能咨询 - 对话记录</h1>
            <p style="text-align: center; color: #6b7280;">导出时间: ${new Date().toLocaleString('zh-CN')}</p><hr>`;

            messages.forEach((msg, msgIndex) => {
                if (msg.role === 'user') {
                    htmlContent += `<div class="user"><strong>您：</strong>${msg.content}</div>`;
                } else {
                    let msgContent = `<div class="assistant"><strong>智能体：</strong><br>${marked.parse(msg.content)}`;

                    // 处理图表导出
                    if (msg.charts && msg.charts.length > 0) {
                        msg.charts.forEach((_, chartIndex) => {
                            // 使用与 ChatWidget 一致的 ID 生成规则
                            const canvasId = `chart-canvas-${msgIndex}-${chartIndex}`;
                            const canvas = document.getElementById(canvasId);
                            if (canvas) {
                                try {
                                    const imgData = canvas.toDataURL('image/png');
                                    msgContent += `<div style="text-align: center; margin: 15px 0;">
                                        <img src="${imgData}" style="max-width: 100%; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                                    </div>`;
                                } catch (e) {
                                    console.error('导出图表失败:', e);
                                }
                            }
                        });
                    }

                    msgContent += `</div>`;
                    htmlContent += msgContent;
                }
            });

            htmlContent += `<div style="text-align:center;color:#9ca3af;margin-top:20px;">本文档由税务智能咨询系统自动生成</div></body></html>`;

            // 3. 写入最终内容
            printWindow.document.open();
            printWindow.document.write(htmlContent);
            printWindow.document.close();

            // 4. 延迟调用打印，确保图片（base64）渲染完成
            setTimeout(() => printWindow.print(), 500);

        } catch (error) {
            console.error('导出PDF出错:', error);
            printWindow.document.body.innerHTML = `<div style="color: red; padding: 20px;">导出失败: ${error.message}</div>`;
        }
    }, [messages]);


    // 选择性删除历史记录 (Sidebar)
    const handleClearHistory = useCallback(async () => {
        // Since history list is derived from messages, deleting history here 
        // implies deleting the messages with that content?
        // Or just hiding it?
        // The implementation in backend is per-message.
        // If we want to delete by "question string", we need to find all messages with that content.

        // Simplified: delete from DB by ID if we can track it, or delete all if "clear all".
        // Use the existing message-based deletion or clear all.

        // Original logic:
        if (selectedHistory.size > 0) {
            if (window.confirm(`确定删除选中的 ${selectedHistory.size} 条历史记录吗？`)) {
                // Delete by content for sidebar
                const contentToDelete = Array.from(selectedHistory);

                const token = localStorage.getItem('access_token');
                await fetch('/api/chat/history', {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': token ? `Bearer ${token}` : ''
                    },
                    body: JSON.stringify({ content_list: contentToDelete, target: 'history' })
                });
                setHistory(prev => prev.filter(h => !selectedHistory.has(h))); // Local update
                setSelectedHistory(new Set());
                // Note: This doesn't affect the main chat window anymore
            }
        } else if (history.length > 0) {
            // Clear all sidebar history
            if (window.confirm('确定要清空所有历史记录吗？')) {
                const token = localStorage.getItem('access_token');
                await fetch('/api/chat/history', {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': token ? `Bearer ${token}` : ''
                    },
                    body: JSON.stringify({ delete_all: true, target: 'history' })
                });
                setHistory([]);
            }
        }
    }, [selectedHistory, history]);

    // 切换历史记录选中状态
    const toggleHistorySelection = (item, e) => {
        e.stopPropagation();
        const newSelected = new Set(selectedHistory);
        if (newSelected.has(item)) {
            newSelected.delete(item);
        } else {
            newSelected.add(item);
        }
        setSelectedHistory(newSelected);
    };

    // 历史记录单击: 循环定位所有回答（最新 -> 上一个 -> ...）
    const handleHistoryClick = (item) => {
        setInputText(item);  // 填充到输入框

        // 1. 找到所有匹配的消息索引
        const indices = [];
        messages.forEach((msg, idx) => {
            if (msg.role === 'user' && msg.content === item) {
                indices.push(idx);
            }
        });

        if (indices.length === 0) return;

        let targetIndex;
        const lastNavIndex = historyNavRef.current[item];

        // 2. 决定跳转目标
        if (indices.length === 1) {
            // 只有一条，直接跳转
            targetIndex = indices[0];
            historyNavRef.current[item] = targetIndex;
        } else {
            // 多条记录，循环逻辑
            if (lastNavIndex === undefined || !indices.includes(lastNavIndex)) {
                // 首次点击或状态失效，定位到最后一条（最新）
                targetIndex = indices[indices.length - 1];
            } else {
                // 不是首次，找当前位置的前一个
                const currentPos = indices.indexOf(lastNavIndex);
                if (currentPos > 0) {
                    targetIndex = indices[currentPos - 1]; // 上一个
                } else {
                    targetIndex = indices[indices.length - 1]; // 循环回到最后一个
                }
            }
            historyNavRef.current[item] = targetIndex;
        }

        // 3. 执行跳转
        if (targetIndex !== undefined && chatWidgetRef.current) {
            chatWidgetRef.current.scrollToMessage(targetIndex);

            // 可选：如果是多条，给个轻提示告诉用户当前是第几条
            // console.log(`Navigated to ${targetIndex}, match ${indices.indexOf(targetIndex) + 1}/${indices.length}`);
        }
    };

    return (
        <div className="ai-chat-page">
            {/* 页面标题栏 */}
            <div className="page-header">
                <div className="page-title">
                    <span className="title-icon">💬</span>
                    <div className="title-text">
                        <h2>AI智能问答</h2>
                        <span className="subtitle">基于专业税务财务知识库的智能问答</span>
                    </div>
                </div>
                <div className="page-actions">
                    <button className="action-btn" onClick={handleClear} disabled={messages.length === 0}>清空对话</button>
                    <button className="action-btn" onClick={handleExportPDF} disabled={messages.length === 0}>导出PDF</button>
                </div>
            </div>

            {/* 主体内容 */}
            <div className="chat-main">
                {/* 对话区域 */}
                <div className="chat-area">
                    <ChatWidget
                        ref={chatWidgetRef}
                        messages={messages}
                        isLoading={isLoading}
                        showChart={responseMode === 'detailed'}

                        // New props for selection mode
                        isSelectionMode={isSelectionMode}
                        selectedIndices={selectedMessageIndices}
                        onToggleSelect={toggleMessageSelection}
                    />

                    {/* 输入区域 (常规模式显示) 或者 操作栏 (选择模式显示) */}
                    {isSelectionMode ? (
                        <div className="input-section selection-bar">
                            <div className="selection-info">
                                已选择 <strong>{selectedMessageIndices.size}</strong> 条消息
                            </div>
                            <div className="selection-actions">
                                <button className="select-action-btn cancel" onClick={toggleSelectionMode}>
                                    取消
                                </button>
                                <button
                                    className="select-action-btn delete"
                                    onClick={handleDeleteSelectedMessages}
                                    disabled={selectedMessageIndices.size === 0}
                                >
                                    🗑️ 删除选中
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="input-section">
                            <div className="input-hint">
                                请输入要咨询的财务指标，或财税政策，或实务操作问题
                            </div>
                            <div className="input-box">
                                <textarea
                                    value={inputText}
                                    onChange={(e) => setInputText(e.target.value)}
                                    onKeyDown={(e) => {
                                        if (e.key === 'Enter' && !e.shiftKey) {
                                            e.preventDefault();
                                            handleSend();
                                        }
                                    }}
                                    placeholder="例如：2022-2025收入、利润变动情况；或小微企业优惠政策有哪些；或小微企业优惠需要申请吗"
                                    disabled={isLoading}
                                    rows={2}
                                />
                                <div className="input-footer">
                                    <div className="input-tools">
                                        {/* 管理消息按钮 - 移到最左侧 */}
                                        <div className="manage-btn-wrapper">
                                            <span
                                                className="tool-btn manage-btn"
                                                onClick={toggleSelectionMode}
                                                title="进入消息选择模式，支持批量删除"
                                            >
                                                ⚙️ 管理消息
                                            </span>
                                        </div>

                                        <div className="mode-toggle">
                                            <span
                                                className={`mode-opt ${responseMode === 'detailed' ? 'active' : ''}`}
                                                onClick={() => setResponseMode('detailed')}
                                                title="全量模式：显示数据表格、图表和AI分析"
                                            >
                                                📊 图文
                                            </span>
                                            <span
                                                className={`mode-opt ${responseMode === 'standard' ? 'active' : ''}`}
                                                onClick={() => setResponseMode('standard')}
                                                title="数据模式：显示数据表格和AI分析，不显示图表"
                                            >
                                                📑 纯数据
                                            </span>
                                            <span
                                                className={`mode-opt ${responseMode === 'concise' ? 'active' : ''}`}
                                                onClick={() => setResponseMode('concise')}
                                                title="简报模式：仅显示AI文字总结"
                                            >
                                                📝 简报
                                            </span>
                                        </div>
                                    </div>

                                    <div className="input-actions">
                                        {/* 上传和语音 - 移到右侧 */}
                                        <span className="tool-btn">📎 上传文档</span>
                                        <span className="tool-btn">🎤 语音输入</span>

                                        <span className="char-count">{inputText.length}/500字符</span>
                                        <span className="input-tip">支持自然语言，逐步响应</span>
                                        <button
                                            className={`submit-btn ${inputText.trim() ? 'active' : ''}`}
                                            onClick={handleSend}
                                            disabled={isLoading || !inputText.trim()}
                                        >
                                            ✨ 提交咨询
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    <div className="disclaimer">
                        AI 智能问答基于 Coze 知识库，回答仅供参考，具体以相关法律法规为准
                    </div>
                </div>

                {/* 右侧历史记录面板 */}
                <div className="history-panel">
                    <div className="history-header">
                        <span className="history-title">📜 历史记录</span>
                        <button className="clear-history-btn" onClick={handleClearHistory}>删除历史</button>
                    </div>
                    <ul className="history-list" ref={historyListRef}>
                        {history.length === 0 ? (
                            <li className="empty-history">暂无历史记录</li>
                        ) : (
                            history.map((item, index) => (
                                <li
                                    key={index}
                                    className={selectedHistory.has(item) ? 'selected' : ''}
                                    onClick={() => handleHistoryClick(item)}
                                    title="单击加载到输入框并定位回答"
                                >
                                    <input
                                        type="checkbox"
                                        checked={selectedHistory.has(item)}
                                        onChange={(e) => toggleHistorySelection(item, e)}
                                        onClick={(e) => e.stopPropagation()}
                                    />
                                    <span>{item.length > 25 ? item.substring(0, 25) + '...' : item}</span>
                                </li>
                            ))
                        )}
                    </ul>
                </div>
            </div>
        </div>
    );
}

export default AIChat;

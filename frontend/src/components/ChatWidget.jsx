import { useState, useEffect, useRef, forwardRef, useImperativeHandle } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import ChartRenderer from './ChartRenderer';
import './ChatWidget.css';

/**
 * 聊天显示组件
 */
const ChatWidget = forwardRef(function ChatWidget({
    messages,
    isLoading,
    showChart = true,
    isSelectionMode = false,
    selectedIndices = new Set(),
    onToggleSelect = () => { }
}, ref) {
    const chatEndRef = useRef(null);
    const containerRef = useRef(null);
    const messageRefs = useRef([]);

    // 滚动状态追踪
    const isUserAtBottomRef = useRef(true);
    const prevIsLoadingRef = useRef(isLoading);

    // 暴露 scrollToMessage 方法给父组件
    useImperativeHandle(ref, () => ({
        scrollToMessage: (index) => {
            if (messageRefs.current[index]) {
                messageRefs.current[index].scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                // 跳转后认为不再底部，或者是特定位置，简单起见暂不强制置为true，由onScroll更新
            }
        }
    }));

    // 监听滚动事件，判断用户是否在底部
    const handleScroll = () => {
        const container = containerRef.current;
        if (container) {
            const { scrollTop, scrollHeight, clientHeight } = container;
            // 阈值设为 50px，在此范围内认为在底部
            isUserAtBottomRef.current = scrollHeight - scrollTop - clientHeight < 50;
        }
    };

    // 智能自动滚动
    useEffect(() => {
        const container = containerRef.current;
        if (!container) return;

        // 1. 响应结束时 (isLoading 从 true -> false)，强制滚动到底部
        if (prevIsLoadingRef.current && !isLoading) {
            chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
        }

        // 2. 正在响应时 (isLoading 为 true)
        else if (isLoading) {
            const lastMsg = messages[messages.length - 1];
            const hasContent = lastMsg && lastMsg.role === 'assistant' && lastMsg.content && lastMsg.content.length > 0;

            if (!hasContent) {
                // 阶段1: 新问题开始，尚未输出流式内容 (Waiting) -> 强制滚动
                chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
                isUserAtBottomRef.current = true;
            } else {
                // 阶段2: 流式显示开始 (Streaming) -> 智能滚动 (仅当用户在底部时)
                if (isUserAtBottomRef.current) {
                    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
                }
            }
        }

        // 3. 开始加载瞬间
        if (!prevIsLoadingRef.current && isLoading) {
            chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
            isUserAtBottomRef.current = true;
        }

        prevIsLoadingRef.current = isLoading;
    }, [messages, isLoading]);

    // 渲染消息内容（支持 Markdown、图表和分析总结）
    const renderMessageContent = (msg, index) => {
        const content = msg.content || '';
        const charts = msg.charts || [];
        const summary = msg.summary || '';

        return (
            <>
                {/* 渲染 Markdown 内容 */}
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {content}
                </ReactMarkdown>

                {/* 渲染图表（根据 showChart 控制） */}
                {showChart && charts.map((chartData, idx) => (
                    <ChartRenderer
                        key={idx}
                        chartData={chartData}
                        canvasId={`chart-canvas-${index}-${idx}`}
                    />
                ))}

                {/* 渲染分析总结（在图表之后） */}
                {summary && (
                    <div className="summary-section">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {summary}
                        </ReactMarkdown>
                    </div>
                )}
            </>
        );
    };

    if (messages.length === 0) {
        return (
            <div className="chat-widget empty">
                <div className="empty-state">
                    <div className="empty-icon">💬</div>
                    <div className="empty-text">开始对话</div>
                    <div className="empty-hint">
                        输入您的问题，如：<br />
                        「高新技术企业有哪些税收优惠？」<br />
                        「2023年营业收入是多少？」
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div
            className={`chat-widget ${isSelectionMode ? 'selection-mode' : ''}`}
            ref={containerRef}
            onScroll={handleScroll}
        >
            {messages.map((msg, index) => {
                const isSelected = selectedIndices.has(index);
                return (
                    <div
                        key={index}
                        className={`chat-message ${msg.role} ${isSelected ? 'selected' : ''}`}
                        ref={el => messageRefs.current[index] = el}
                        onClick={() => isSelectionMode && onToggleSelect(index)}
                    >
                        {isSelectionMode && (
                            <div className="selection-checkbox">
                                <input
                                    type="checkbox"
                                    checked={isSelected}
                                    readOnly
                                />
                            </div>
                        )}

                        {msg.role === 'user' ? (
                            <div className="user-message">
                                <span className="timestamp">[{msg.timestamp}]</span>
                                <strong>您：</strong>
                                {msg.content}
                            </div>
                        ) : (
                            <div className="assistant-message">
                                <div className="message-header">
                                    <strong>智能体：</strong>
                                    {msg.route && (
                                        <span className={`route-badge ${msg.route}`}>
                                            {msg.route === 'financial' && '📊 财务数据'}
                                            {msg.route === 'tax_incentive' && '📋 税收优惠'}
                                            {msg.route === 'coze' && '🤖 知识库'}
                                            {msg.route === 'financial_data' && '📊 财务数据'}
                                        </span>
                                    )}
                                </div>
                                <div className="message-content">
                                    {renderMessageContent(msg, index)}
                                </div>
                                {!isLoading && msg.content && !isSelectionMode && (
                                    <div className="message-actions">
                                        <button
                                            className="copy-btn"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                navigator.clipboard.writeText(msg.content);
                                            }}
                                        >
                                            📋 复制回答
                                        </button>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                );
            })}

            {isLoading && (
                <div className="loading-indicator">
                    <span className="loading-dot"></span>
                    <span className="loading-dot"></span>
                    <span className="loading-dot"></span>
                </div>
            )}

            <div ref={chatEndRef} />
        </div>
    );
});

export default ChatWidget;

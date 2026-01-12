import { useState, useEffect, useRef, forwardRef, useImperativeHandle } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import ChartRenderer from './ChartRenderer';
import './ChatWidget.css';

/**
 * 聊天显示组件
 */
const ChatWidget = forwardRef(function ChatWidget({ messages, isLoading, showChart = true }, ref) {
    const chatEndRef = useRef(null);
    const containerRef = useRef(null);
    const messageRefs = useRef([]);

    // 暴露 scrollToMessage 方法给父组件
    useImperativeHandle(ref, () => ({
        scrollToMessage: (index) => {
            if (messageRefs.current[index]) {
                messageRefs.current[index].scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }
    }));

    // 自动滚动到底部
    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

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
        <div className="chat-widget" ref={containerRef}>
            {messages.map((msg, index) => (
                <div
                    key={index}
                    className={`chat-message ${msg.role}`}
                    ref={el => messageRefs.current[index] = el}
                >
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
                            {!isLoading && msg.content && (
                                <div className="message-actions">
                                    <button
                                        className="copy-btn"
                                        onClick={() => {
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
            ))}

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

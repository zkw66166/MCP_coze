import { useState, useRef } from 'react';
import './InputWidget.css';

/**
 * 输入组件
 */
function InputWidget({
    companies,
    selectedCompanyId,
    onCompanyChange,
    onSend,
    isLoading,
    history,
    onHistoryClick,
    onHistoryDoubleClick,
    onClearHistory
}) {
    const [inputText, setInputText] = useState('');
    const textareaRef = useRef(null);

    // 处理发送
    const handleSend = () => {
        const text = inputText.trim();
        if (text && !isLoading) {
            onSend(text);
            setInputText('');
        }
    };

    // 快捷键支持
    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    // 双击历史记录：填充到输入框
    const handleDoubleClick = (item) => {
        setInputText(item);
        onHistoryDoubleClick?.(item);
    };

    // 获取选中的公司名称
    const selectedCompany = companies.find(c => c.id === selectedCompanyId);

    return (
        <div className="input-widget">
            {/* 公司选择 */}
            <div className="company-selector">
                <label>🏢 查询企业:</label>
                <select
                    value={selectedCompanyId || ''}
                    onChange={(e) => onCompanyChange(Number(e.target.value) || null)}
                >
                    {companies.map(company => (
                        <option key={company.id} value={company.id}>
                            {company.name}
                        </option>
                    ))}
                </select>
            </div>

            <div className="separator"></div>

            {/* 输入区域 */}
            <div className="input-area">
                <label>📝 输入问题 (财务数据/税收优惠/通用咨询)</label>
                <textarea
                    ref={textareaRef}
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="如: 2023年利润率? / 小微企业优惠政策有哪些?"
                    disabled={isLoading}
                    rows={3}
                />

                <div className="button-row">
                    <button
                        className="send-btn"
                        onClick={handleSend}
                        disabled={isLoading || !inputText.trim()}
                    >
                        {isLoading ? '⏳ 处理中...' : '📤 发送'}
                    </button>
                </div>
            </div>

            {/* 历史记录 */}
            <div className="history-section">
                <div className="history-header">
                    <span>📜 历史记录</span>
                    <button
                        className="clear-history-btn"
                        onClick={onClearHistory}
                        disabled={history.length === 0}
                    >
                        删除记录
                    </button>
                </div>
                <ul className="history-list">
                    {history.length === 0 ? (
                        <li className="empty-history">暂无历史记录</li>
                    ) : (
                        history.map((item, index) => (
                            <li
                                key={index}
                                onClick={() => onHistoryClick(item)}
                                onDoubleClick={() => handleDoubleClick(item)}
                                title="单击定位到回答，双击填充到输入框"
                            >
                                {item.length > 40 ? item.substring(0, 40) + '...' : item}
                            </li>
                        ))
                    )}
                </ul>
            </div>
        </div>
    );
}

export default InputWidget;

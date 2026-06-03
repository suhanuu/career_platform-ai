/**
 * ============================================
 * 「职引未来」AI对话模块
 * 聊天气泡 + 打字机效果 + 历史记录管理
 * ============================================
 */

// ===== 对话状态 =====
let chatHistory = [];     // [{role, content}, ...]
let isChatting = false;   // 防止重复发送

// ===== 从后端加载历史记录 =====
async function loadChatHistory() {
    if (!Auth.isLoggedIn()) return;

    try {
        const res = await fetch(API_BASE + '/chat/history', {
            headers: { 'Authorization': 'Bearer ' + Auth.token },
        });
        if (!res.ok) return;
        const data = await res.json();

        if (data.history && data.history.length > 0) {
            chatHistory = data.history;
            const welcome = document.getElementById('chat-welcome');
            const messagesContainer = document.getElementById('chat-messages');
            welcome.style.display = 'none';
            messagesContainer.style.display = 'flex';
            messagesContainer.innerHTML = '';

            data.history.forEach(msg => {
                appendMessage(msg.role, msg.content);
            });
            scrollToBottom();
        }
    } catch (err) {
        console.error('加载历史记录失败:', err);
    }
}

// ===== 聊天输入框 =====
function initChatInput() {
    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('chat-send-btn');
    const clearBtn = document.getElementById('chat-clear-btn');

    // 回车发送 (Shift+Enter 换行)
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // 自动调整输入框高度
    input.addEventListener('input', () => {
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 120) + 'px';
    });

    sendBtn.addEventListener('click', sendMessage);
    clearBtn.addEventListener('click', clearChat);
}

// ===== 欢迎页快捷提问 =====
function initWelcomeSuggestions() {
    document.querySelectorAll('.suggestion-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const msg = chip.dataset.msg;
            document.getElementById('chat-input').value = msg;
            sendMessage();
        });
    });
}

// ===== 发送消息 =====
async function sendMessage() {
    if (isChatting) return;

    // 未登录拦截
    if (!Auth.isLoggedIn()) {
        showToast('请先登录后再使用AI对话', 'error');
        document.getElementById('login-btn').click();
        return;
    }

    const input = document.getElementById('chat-input');
    const message = input.value.trim();

    if (!message) return;
    if (message.length > 2000) {
        showToast('消息过长，最多2000字', 'error');
        return;
    }

    // 隐藏欢迎界面
    const welcome = document.getElementById('chat-welcome');
    const messagesContainer = document.getElementById('chat-messages');
    welcome.style.display = 'none';
    messagesContainer.style.display = 'flex';

    // 渲染用户消息
    appendMessage('user', message);
    chatHistory.push({ role: 'user', content: message });

    // 清空输入框
    input.value = '';
    input.style.height = 'auto';

    // 禁用发送
    isChatting = true;
    document.getElementById('chat-send-btn').disabled = true;

    // 显示AI加载气泡
    const loadingBubble = appendLoadingBubble();

    try {
        // 调用后端API (携带JWT)
        const res = await fetch(API_BASE + '/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + Auth.token,
            },
            body: JSON.stringify({
                message: message,
                history: chatHistory.slice(0, -1),
            }),
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: '请求失败' }));
            if (res.status === 401) {
                Auth.logout();
                throw new Error('登录已过期，请重新登录');
            }
            throw new Error(err.detail || `HTTP ${res.status}`);
        }

        const data = await res.json();

        // 移除加载气泡
        loadingBubble.remove();

        // 打字机效果渲染AI回复
        chatHistory.push({ role: 'assistant', content: data.reply });
        await typewriterEffect(data.reply, messagesContainer);

    } catch (err) {
        loadingBubble.remove();
        appendMessage('assistant', '抱歉，AI服务暂时不可用，请稍后重试 😥\n\n> ' + err.message);
        showToast(err.message || 'AI服务异常', 'error');
        console.error('Chat error:', err);
    }

    isChatting = false;
    document.getElementById('chat-send-btn').disabled = false;
    input.focus();
}

// ===== 渲染消息气泡 =====
function appendMessage(role, content) {
    const messagesContainer = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = `message ${role}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? '👤' : '🤖';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.innerHTML = formatMessage(content);

    div.appendChild(avatar);
    div.appendChild(bubble);
    messagesContainer.appendChild(div);
    scrollToBottom();

    return div;
}

// ===== 加载中气泡 =====
function appendLoadingBubble() {
    const messagesContainer = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = 'message assistant';
    div.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-bubble typing-cursor">思考中</div>
    `;
    messagesContainer.appendChild(div);
    scrollToBottom();
    return div;
}

// ===== 打字机效果 =====
async function typewriterEffect(text, container) {
    const div = document.createElement('div');
    div.className = 'message assistant';

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = '🤖';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.innerHTML = '';

    div.appendChild(avatar);
    div.appendChild(bubble);
    container.appendChild(div);

    // 解析 Markdown 后再逐字显示
    const formatted = formatMessage(text);
    // 如果文本较短（<100字），用打字机效果；否则直接显示
    if (text.length < 150) {
        bubble.innerHTML = '<span class="typing-cursor"></span>';
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = formatted;
        const plainText = tempDiv.textContent || '';

        let i = 0;
        const interval = setInterval(() => {
            if (i < plainText.length) {
                bubble.innerHTML = escapeHtml(plainText.substring(0, i + 1)) + '<span class="typing-cursor"></span>';
                i++;
                scrollToBottom();
            } else {
                clearInterval(interval);
                bubble.innerHTML = formatted; // 最终显示格式化后的Markdown
                scrollToBottom();
            }
        }, 30);
    } else {
        bubble.innerHTML = formatted;
        scrollToBottom();
    }
}

// ===== 简单 Markdown 格式化 =====
function formatMessage(text) {
    // 转义HTML (保留我们要用的)
    let html = escapeHtml(text);

    // 加粗 **text**
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    // 列表项 - 或 1.
    html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
    html = html.replace(/^\d+\.\s(.+)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');

    // 换行
    html = html.replace(/\n/g, '<br>');

    return html;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ===== 滚动到底部 =====
function scrollToBottom() {
    const container = document.getElementById('chat-messages');
    if (container) {
        setTimeout(() => {
            container.scrollTop = container.scrollHeight;
        }, 50);
    }
}

// ===== 清空对话 =====
async function clearChat() {
    if (chatHistory.length === 0) return;
    if (!confirm('确定要清空所有对话记录吗？')) return;

    chatHistory = [];
    document.getElementById('chat-messages').innerHTML = '';
    document.getElementById('chat-messages').style.display = 'none';
    document.getElementById('chat-welcome').style.display = 'flex';

    // 同步删除后端记录
    if (Auth.isLoggedIn()) {
        try {
            await fetch(API_BASE + '/chat/history', {
                method: 'DELETE',
                headers: { 'Authorization': 'Bearer ' + Auth.token },
            });
        } catch (err) {
            console.error('清空后端记录失败:', err);
        }
    }

    showToast('对话已清空', 'success');
}

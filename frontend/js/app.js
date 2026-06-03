/**
 * ============================================
 * 「职引未来」主逻辑
 * Tab切换 + 页面初始化 + 全局工具函数
 * ============================================
 */

// ===== 全局状态 =====
const API_BASE = '/api';

// ===== 页面初始化 =====
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initChatInput();
    initWelcomeSuggestions();
    loadSkills(); // 预加载技能标签到匹配页

    // 如果 URL 带 ?tab=match 则直接跳匹配页
    const params = new URLSearchParams(window.location.search);
    if (params.get('tab') === 'match') {
        switchTab('match');
    }
});

// ===== Tab 切换 =====
function initTabs() {
    const navBtns = document.querySelectorAll('.nav-btn');
    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // 更新导航按钮状态
    document.querySelectorAll('.nav-btn').forEach(b => {
        b.classList.toggle('active', b.dataset.tab === tabName);
    });
    // 更新内容区显示
    document.querySelectorAll('.tab-content').forEach(c => {
        c.classList.toggle('active', c.id === `tab-${tabName}`);
    });
    // 切换到匹配页时重绘雷达图
    if (tabName === 'match') {
        setTimeout(resizeAllRadarCharts, 100);
    }
}

// ===== Toast 提示 =====
let toastTimer = null;
function showToast(msg, type = '') {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.className = 'toast ' + type + ' show';
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
        toast.classList.remove('show');
    }, 2500);
}

// ===== 加载动画 =====
function showLoading(text = '加载中...') {
    const overlay = document.getElementById('loading-overlay');
    overlay.querySelector('p').textContent = text;
    overlay.style.display = 'flex';
}
function hideLoading() {
    document.getElementById('loading-overlay').style.display = 'none';
}

// ===== 通用 API 请求 =====
async function apiGet(path) {
    const res = await fetch(API_BASE + path);
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: '请求失败' }));
        throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
}

async function apiPost(path, body) {
    const res = await fetch(API_BASE + path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: '请求失败' }));
        throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
}

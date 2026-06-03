/**
 * ============================================
 * 「职引未来」用户认证模块
 * 登录/注册弹窗 + Token管理 + 全局Auth状态
 * ============================================
 */

// ===== 全局 Auth 状态 =====
const Auth = {
    token: localStorage.getItem('auth_token') || '',
    user: null,

    // 从 localStorage 恢复登录状态
    restore() {
        this.token = localStorage.getItem('auth_token') || '';
        const savedUser = localStorage.getItem('auth_user');
        if (savedUser) {
            try { this.user = JSON.parse(savedUser); } catch(e) { this.user = null; }
        }
    },

    // 保存登录状态
    save(token, user) {
        this.token = token;
        this.user = user;
        localStorage.setItem('auth_token', token);
        localStorage.setItem('auth_user', JSON.stringify(user));
        updateHeaderUI();
        // 登录后加载云端对话历史
        setTimeout(() => loadChatHistory(), 300);
    },

    // 退出登录
    logout() {
        this.token = '';
        this.user = null;
        localStorage.removeItem('auth_token');
        localStorage.removeItem('auth_user');
        updateHeaderUI();
        // 清空本地对话状态
        chatHistory = [];
        const welcome = document.getElementById('chat-welcome');
        const messagesContainer = document.getElementById('chat-messages');
        if (messagesContainer) messagesContainer.innerHTML = '';
        if (messagesContainer) messagesContainer.style.display = 'none';
        if (welcome) welcome.style.display = 'flex';
        showToast('已退出登录', 'success');
    },

    // 是否已登录
    isLoggedIn() {
        return !!this.token;
    },

    // 获取 Authorization header
    getAuthHeader() {
        return this.token ? { 'Authorization': 'Bearer ' + this.token } : {};
    }
};

// ===== 初始化 =====
document.addEventListener('DOMContentLoaded', () => {
    Auth.restore();
    updateHeaderUI();
    initAuthModal();
});

// ===== 更新头部 UI（登录按钮 ↔ 用户信息）=====
function updateHeaderUI() {
    const loginBtn = document.getElementById('login-btn');
    const userInfo = document.getElementById('user-info');
    const userName = document.getElementById('user-name');

    if (Auth.isLoggedIn() && Auth.user) {
        loginBtn.style.display = 'none';
        userInfo.style.display = 'flex';
        userName.textContent = Auth.user.username;
    } else {
        loginBtn.style.display = '';
        userInfo.style.display = 'none';
        userName.textContent = '';
    }
}

// ===== 弹窗逻辑 =====
function initAuthModal() {
    const modal = document.getElementById('auth-modal');
    const loginBtn = document.getElementById('login-btn');
    const closeBtn = modal.querySelector('.auth-modal-close');
    const tabBtns = modal.querySelectorAll('.auth-tab');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    // 打开弹窗
    loginBtn.addEventListener('click', () => {
        modal.style.display = 'flex';
        document.getElementById('login-error').style.display = 'none';
        document.getElementById('register-error').style.display = 'none';
    });

    // 关闭弹窗
    closeBtn.addEventListener('click', () => { modal.style.display = 'none'; });
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.style.display = 'none';
    });

    // Tab 切换
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const tab = btn.dataset.authTab;
            loginForm.style.display = tab === 'login' ? '' : 'none';
            loginForm.classList.toggle('active', tab === 'login');
            registerForm.style.display = tab === 'register' ? '' : 'none';
            registerForm.classList.toggle('active', tab === 'register');
        });
    });

    // 登录提交
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('login-username').value.trim();
        const password = document.getElementById('login-password').value;
        const errorEl = document.getElementById('login-error');

        if (!username || !password) {
            errorEl.textContent = '请填写用户名和密码';
            errorEl.style.display = 'block';
            return;
        }

        try {
            const data = await apiPost('/auth/login', { username, password });
            Auth.save(data.token, data.user);
            modal.style.display = 'none';
            loginForm.reset();
            errorEl.style.display = 'none';
            showToast(`欢迎回来，${data.user.username}！`, 'success');
        } catch (err) {
            errorEl.textContent = err.message || '登录失败';
            errorEl.style.display = 'block';
        }
    });

    // 注册提交
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('reg-username').value.trim();
        const password = document.getElementById('reg-password').value;
        const email = document.getElementById('reg-email').value.trim();
        const errorEl = document.getElementById('register-error');

        if (username.length < 2) {
            errorEl.textContent = '用户名至少2个字符';
            errorEl.style.display = 'block';
            return;
        }
        if (password.length < 6) {
            errorEl.textContent = '密码至少6位';
            errorEl.style.display = 'block';
            return;
        }

        try {
            const data = await apiPost('/auth/register', { username, password, email });
            Auth.save(data.token, data.user);
            modal.style.display = 'none';
            registerForm.reset();
            errorEl.style.display = 'none';
            showToast(`注册成功！欢迎加入，${data.user.username}！`, 'success');
        } catch (err) {
            errorEl.textContent = err.message || '注册失败';
            errorEl.style.display = 'block';
        }
    });

    // 退出按钮
    document.getElementById('logout-btn').addEventListener('click', () => {
        Auth.logout();
    });
}

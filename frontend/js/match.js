/**
 * ============================================
 * 「职引未来」技能匹配模块
 * 技能标签云 + 匹配结果 + ECharts雷达图
 * ============================================
 */

// ===== 状态 =====
let selectedSkills = new Set();     // 用户选中的技能ID
let allSkills = [];                 // 全部技能列表
let matchResultsData = [];          // 匹配结果缓存
let radarCharts = {};               // 存储雷达图实例

// ===== 加载技能标签 =====
async function loadSkills() {
    try {
        const data = await apiGet('/skills');
        allSkills = data.data || [];
        renderSkillCloud(allSkills);
    } catch (err) {
        console.error('加载技能失败:', err);
        showToast('加载技能列表失败，请刷新页面', 'error');
    }
}

function renderSkillCloud(skills) {
    const hardContainer = document.getElementById('hard-skills-cloud');
    const softContainer = document.getElementById('soft-skills-cloud');

    hardContainer.innerHTML = '';
    softContainer.innerHTML = '';

    skills.forEach(skill => {
        const tag = document.createElement('span');
        tag.className = 'skill-tag';
        tag.textContent = skill.name;
        tag.dataset.skillId = skill.id;
        tag.addEventListener('click', () => toggleSkill(skill.id, tag));

        if (skill.category === 'hard') {
            hardContainer.appendChild(tag);
        } else {
            softContainer.appendChild(tag);
        }
    });
}

// ===== 切换技能选择 =====
function toggleSkill(skillId, tagElement) {
    if (selectedSkills.has(skillId)) {
        selectedSkills.delete(skillId);
        tagElement.classList.remove('selected');
    } else {
        if (selectedSkills.size >= 20) {
            showToast('最多选择20个技能', 'error');
            return;
        }
        selectedSkills.add(skillId);
        tagElement.classList.add('selected');
    }

    // 更新计数
    document.getElementById('selected-count').textContent = selectedSkills.size;

    // 更新按钮状态
    const matchBtn = document.getElementById('match-btn');
    matchBtn.disabled = selectedSkills.size < 1;
    if (selectedSkills.size >= 1) {
        matchBtn.innerHTML = '<span class="btn-icon">🔍</span> 开始匹配';
    }
}

// ===== 执行匹配 =====
document.getElementById('match-btn').addEventListener('click', async () => {
    if (selectedSkills.size < 1) {
        showToast('请至少选择1个技能', 'error');
        return;
    }

    // 未登录拦截
    if (!Auth.isLoggedIn()) {
        showToast('请先登录后再使用技能匹配', 'error');
        document.getElementById('login-btn').click();
        return;
    }

    showLoading('正在分析匹配...');

    try {
        const res = await fetch(API_BASE + '/match', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + Auth.token,
            },
            body: JSON.stringify({ skill_ids: Array.from(selectedSkills) }),
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

        matchResultsData = data.results || [];
        renderResults(matchResultsData);

    } catch (err) {
        showToast('匹配失败，请稍后重试', 'error');
        console.error('匹配失败:', err);
    }

    hideLoading();
});

// ===== 渲染匹配结果 =====
function renderResults(results) {
    const placeholder = document.getElementById('match-placeholder');
    const resultsContainer = document.getElementById('match-results');

    placeholder.style.display = 'none';
    resultsContainer.style.display = 'flex';
    resultsContainer.innerHTML = '';

    // 清除旧雷达图
    Object.values(radarCharts).forEach(chart => chart.dispose());
    radarCharts = {};

    if (results.length === 0) {
        resultsContainer.innerHTML = `
            <div class="match-placeholder" style="height:auto; padding:40px;">
                <div class="placeholder-icon">🤔</div>
                <h3>未找到匹配的岗位</h3>
                <p>尝试选择更多技能，特别是硬技能</p>
            </div>`;
        return;
    }

    results.forEach((result, index) => {
        const card = createResultCard(result, index);
        resultsContainer.appendChild(card);

        // 渲染雷达图
        const chartDom = card.querySelector('.radar-chart');
        if (chartDom) {
            renderRadarChart(chartDom, result);
        }
    });
}

// ===== 创建结果卡片 =====
function createResultCard(result, index) {
    const card = document.createElement('div');
    card.className = 'result-card';

    const job = result.job;
    const rate = result.match_rate;
    const rateColor = rate >= 70 ? '#10B981' : rate >= 45 ? '#F59E0B' : '#EF4444';
    const rankLabels = ['🥇', '🥈', '🥉', '④', '⑤'];

    // 差距标签
    const gapsHtml = result.skill_gaps
        .sort((a, b) => b.importance - a.importance)
        .map(g => {
            const cls = g.user_has ? 'matched' : 'missing';
            const icon = g.user_has ? '✅' : '❌';
            const stars = '★'.repeat(g.importance) + '☆'.repeat(5 - g.importance);
            return `<span class="gap-tag ${cls}">
                ${icon} ${g.skill_name}
                <span class="gap-importance">${stars}</span>
            </span>`;
        })
        .join('');

    card.innerHTML = `
        <div class="result-card-header">
            <span class="result-card-rank">${rankLabels[index] || '#' + (index + 1)}</span>
            <span class="job-title">${job.title}</span>
            <div class="match-rate">
                <div class="match-rate-circle">
                    <svg width="50" height="50" viewBox="0 0 50 50">
                        <circle cx="25" cy="25" r="22" fill="none" stroke="#E2E8F0" stroke-width="4"/>
                        <circle cx="25" cy="25" r="22" fill="none" stroke="${rateColor}"
                            stroke-width="4" stroke-linecap="round"
                            stroke-dasharray="${rate * 1.38} 138"
                            stroke-dashoffset="0"/>
                    </svg>
                    <span class="rate-text" style="color:${rateColor}">${rate}%</span>
                </div>
            </div>
        </div>
        <div class="result-card-body">
            <div class="job-meta">
                <span class="job-meta-tag industry">🏭 ${job.industry}</span>
                <span class="job-meta-tag">💰 ${job.salary_min}K-${job.salary_max}K/月</span>
                <span class="job-meta-tag">🎓 ${job.education}</span>
                <span class="job-meta-tag">⏱ ${job.experience}</span>
            </div>
            <p style="font-size:13px;color:#64748B;line-height:1.7;margin-bottom:16px;">${job.description}</p>
            <div class="radar-chart" id="radar-${job.id}"></div>
            <h4 style="font-size:14px;margin:12px 0 8px;color:#1E293B;">📋 技能匹配详情</h4>
            <div class="skill-gaps">${gapsHtml}</div>
        </div>
    `;

    return card;
}

// ===== 渲染 ECharts 雷达图 =====
function renderRadarChart(dom, result) {
    const rd = result.radar_data;
    const chart = echarts.init(dom);

    const option = {
        tooltip: {
            trigger: 'item',
        },
        legend: {
            data: ['你的技能', '岗位要求'],
            bottom: 5,
            textStyle: { fontSize: 11 },
        },
        radar: {
            center: ['50%', '50%'],
            radius: '65%',
            indicator: rd.labels.map(name => ({
                name: name,
                max: 5,
            })),
            axisName: {
                fontSize: 10,
                color: '#64748B',
            },
            shape: 'polygon',
            splitNumber: 4,
            axisNameGap: 8,
        },
        series: [{
            type: 'radar',
            data: [
                {
                    value: rd.job_values,
                    name: '岗位要求',
                    symbol: 'diamond',
                    symbolSize: 6,
                    lineStyle: { color: '#94A3B8', width: 2, type: 'dashed' },
                    areaStyle: { color: 'rgba(148,163,184,0.08)' },
                    itemStyle: { color: '#94A3B8' },
                },
                {
                    value: rd.user_values,
                    name: '你的技能',
                    symbol: 'circle',
                    symbolSize: 7,
                    lineStyle: { color: '#4F6EF7', width: 2.5 },
                    areaStyle: { color: 'rgba(79,110,247,0.15)' },
                    itemStyle: { color: '#4F6EF7' },
                },
            ],
        }],
    };

    chart.setOption(option);
    radarCharts[result.job.id] = chart;

    // 响应式调整
    window.addEventListener('resize', () => chart.resize());
}

// ===== 切换Tab时重绘雷达图 =====
function resizeAllRadarCharts() {
    Object.values(radarCharts).forEach(chart => {
        if (chart && !chart.isDisposed()) {
            chart.resize();
        }
    });
}

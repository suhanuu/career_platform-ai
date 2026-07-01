# 职引未来 — AI职业规划与技能匹配平台 帮助文档

---

## 一、项目概述

**职引未来** 是一个 AI 驱动的大学生职业规划与技能匹配平台，基于 FastAPI + MySQL 构建。

### 核心功能

| 功能 | 说明 |
|------|------|
| AI 职业对话 | 基于 DeepSeek 大模型，为用户提供个性化职业规划建议 |
| 技能匹配 | 根据用户已掌握的技能，智能匹配最适合的岗位，展示匹配度与技能差距 |
| 岗位数据 | 支持从实习僧、Boss 直聘等平台爬取真实岗位数据 |
| 用户认证 | 注册/登录，JWT 令牌认证 |

### 系统架构

```
┌─────────────────────────────────────────────────────┐
│                    前端 (纯静态 HTML/CSS/JS)          │
│                  端口: FastAPI 静态文件服务            │
├─────────────────────────────────────────────────────┤
│                    FastAPI 后端服务                   │
│                  端口: 8000                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │ AI对话   │ │ 技能匹配  │ │ 数据接口  │ │ 用户认证│ │
│  │ /api/chat│ │ /api/match│ │/api/data  │ │/api/auth│ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └───┬────┘ │
│       │             │            │            │      │
├───────┼─────────────┼────────────┼────────────┼──────┤
│       ▼             ▼            ▼            ▼      │
│  ┌────────────────────────────────────────────────┐  │
│  │  DeepSeek API  │  MySQL (aiomysql) │  JWT     │  │
│  │   (AI 推理)    │  (数据存储)       │ (身份认证) │  │
│  └────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## 二、技术栈

| 技术/框架 | 版本 | 用途 |
|-----------|------|------|
| Python | 3.12+ | 开发语言 |
| FastAPI | 0.115.6 | Web 框架（异步、高性能） |
| Uvicorn | 0.34.0 | ASGI 服务器（支持热重载） |
| aiomysql | 0.2.0 | 异步 MySQL 驱动 |
| PyMySQL | 1.1.1 | 同步 MySQL 驱动（爬虫脚本用） |
| httpx | 0.28.1 | 异步 HTTP 客户端（调用 DeepSeek API） |
| Pydantic | 2.10.4 | 数据验证与序列化 |
| bcrypt | 4.2.1 | 密码哈希加密 |
| python-jose | 3.3.0 | JWT 令牌签发与校验 |
| DeepSeek API | — | AI 对话引擎（deepseek-chat 模型） |
| MySQL | — | 主数据库（`career_platform`） |
| ECharts | 5.5.0 | 前端图表库（雷达图等） |

---

## 三、项目结构

```
career-platform/
├── backend/                        # 后端（FastAPI 服务）
│   ├── main.py                     # 启动入口（FastAPI 应用创建、路由注册、生命周期）
│   ├── config.py                   # 全局配置（DeepSeek API、MySQL、JWT、CORS）
│   ├── database.py                 # MySQL 异步连接池 + 自动建表 + 种子数据
│   ├── requirements.txt            # Python 依赖
│   ├── models/
│   │   └── schemas.py              # Pydantic 请求/响应模型
│   ├── routes/                     # API 路由（4 个模块）
│   │   ├── auth.py                 # 用户认证（注册/登录/获取当前用户）
│   │   ├── chat.py                 # AI 对话（发消息、获取历史、清空历史）
│   │   ├── match.py                # 技能匹配（智能匹配算法）
│   │   └── data.py                 # 数据接口（获取技能列表、岗位列表）
│   ├── services/                   # 业务逻辑层
│   │   ├── auth_service.py         # 密码哈希 + JWT 签发/校验
│   │   ├── llm_service.py          # DeepSeek API 调用封装
│   │   └── match_service.py        # 技能-岗位匹配算法（加权 Jaccard）
│   └── scraper/                    # 爬虫模块（数据采集）
│       ├── shixiseng.py            # 实习僧爬虫
│       ├── boss.py                 # Boss 直聘爬虫
│       ├── import_to_db.py         # 爬取数据导入 MySQL
│       └── run_all.py              # 一键运行所有爬虫 + 导入
├── frontend/                       # 前端（纯静态页面）
│   ├── index.html                  # 单页应用入口
│   ├── css/
│   │   └── style.css               # 样式文件
│   └── js/
│       ├── app.js                  # 主应用逻辑（Tab 切换）
│       ├── auth.js                 # 登录/注册弹窗逻辑
│       ├── chat.js                 # AI 对话页面交互
│       └── match.js                # 技能匹配页面交互
├── data/                           # 爬虫数据缓存（JSON 文件）
│   ├── shixiseng_jobs.json
│   ├── boss_jobs.json
│   └── fallback_jobs.json          # 爬虫失败时的备用数据
└── sql/
    └── init.sql                    # 数据库建表 + 种子数据（SQL 脚本）
```

---

## 四、数据库设计

### 数据表结构

#### 1. skills（技能表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT (PK, AI) | 主键 |
| name | VARCHAR(50) | 技能名称 |
| category | VARCHAR(20) | 技能类别：`hard`（硬技能）/ `soft`（软技能） |
| created_at | DATETIME | 创建时间 |

**种子数据**：30 个技能（硬技能 15 个 + 软技能 15 个）

#### 2. jobs（岗位表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT (PK, AI) | 主键 |
| title | VARCHAR(100) | 岗位名称 |
| description | TEXT | 岗位描述 |
| industry | VARCHAR(50) | 所属行业（互联网/IT、金融、制造业、教育/咨询、电商/新媒体） |
| salary_min | INT | 最低月薪（千元） |
| salary_max | INT | 最高月薪（千元） |
| education | VARCHAR(20) | 学历要求 |
| experience | VARCHAR(20) | 经验要求 |
| created_at | DATETIME | 创建时间 |

**种子数据**：15 个岗位，覆盖 5 个行业

#### 3. job_skills（岗位-技能关联表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT (PK, AI) | 主键 |
| job_id | INT (FK) | 关联岗位 ID |
| skill_id | INT (FK) | 关联技能 ID |
| importance | TINYINT | 重要度 1-5（5 = 必备，3 = 加分项） |

**种子数据**：107 条关联记录

#### 4. users（用户表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT (PK, AI) | 主键 |
| username | VARCHAR(50) (UNIQUE) | 用户名 |
| password_hash | VARCHAR(255) | 加密密码 |
| email | VARCHAR(100) | 邮箱 |
| created_at | DATETIME | 注册时间 |

#### 5. chat_history（对话历史表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT (PK, AI) | 主键 |
| user_id | INT (FK) | 关联用户 ID |
| role | VARCHAR(10) | 角色：`user` / `assistant` |
| content | TEXT | 消息内容 |
| created_at | DATETIME | 发送时间 |

### 数据关系图

```
users (1) ──→ (N) chat_history
skills (1) ──→ (N) job_skills (N) ──→ (1) jobs
```

---

## 五、功能模块详解

### 5.1 AI 职业对话（/api/chat）

| 接口 | 方法 | 说明 | 认证 |
|------|------|------|------|
| `/api/chat` | POST | 发送消息给 AI，自动保存对话历史 | 需要 |
| `/api/chat/history` | GET | 获取当前用户的完整对话历史 | 需要 |
| `/api/chat/history` | DELETE | 清空当前用户的对话历史 | 需要 |

**实现细节**：
- 调用 DeepSeek API（`deepseek-chat` 模型）
- 系统角色设定为资深职业规划师，提供专业、可落地的职业建议
- 保留最近 20 轮对话历史，避免 Token 超限
- 对话内容自动存入 MySQL `chat_history` 表

### 5.2 技能匹配（/api/match）

| 接口 | 方法 | 说明 | 认证 |
|------|------|------|------|
| `/api/match` | POST | 提交技能列表，获取匹配度最高的 Top 5 岗位 | 需要 |

**匹配算法 — 加权 Jaccard 相似度**：

```
硬技能权重 0.7 + 软技能权重 0.3

匹配度 = (硬技能交集权重 / 硬技能并集权重) × 0.7
       + (软技能交集权重 / 软技能并集权重) × 0.3
```

**返回结果包含**：
- 岗位信息（名称、行业、薪资、学历要求等）
- 匹配度百分比（0-100）
- 雷达图数据（用户 vs 岗位要求的前 6 项重要技能对比）
- 技能差距分析（逐项列出用户是否具备，重要度如何）

### 5.3 数据接口（/api/data — 无需认证）

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/skills` | GET | 获取全部 30 个技能列表（供前端标签云展示） |
| `/api/jobs` | GET | 获取全部岗位列表 |

### 5.4 用户认证（/api/auth — 无需认证）

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/auth/register` | POST | 用户注册（用户名 + 密码 + 邮箱） |
| `/api/auth/login` | POST | 用户登录，返回 JWT 令牌 |
| `/api/auth/me` | GET | 获取当前登录用户信息 |

**认证方式**：
- 密码使用 bcrypt 哈希存储
- JWT 令牌有效期 24 小时
- 请求时在 Header 中携带：`Authorization: Bearer <token>`

### 5.5 爬虫系统（scraper/）

| 脚本 | 说明 |
|------|------|
| `shixiseng.py` | 爬取实习僧平台的实习岗位（12 个关键词搜索） |
| `boss.py` | 爬取 Boss 直聘的实习岗位（12 个关键词搜索） |
| `import_to_db.py` | 将爬取的 JSON 数据导入 MySQL，自动匹配技能标签 |
| `run_all.py` | 一键运行所有爬虫 + 导入数据库，含备用数据兜底 |

**爬虫特性**：
- 浏览器 User-Agent 伪装
- 关键词搜索策略
- 自动去重
- 反爬容错（失败自动使用内置备用数据）
- 礼貌延迟（避免被封）

---

## 六、前端架构

### 单页应用（SPA）

纯原生 HTML/CSS/JavaScript 实现，无需构建工具。

**页面结构**：

| 区域 | 功能 |
|------|------|
| 顶部导航 | 切换「AI 职业对话」和「技能匹配」两个 Tab |
| AI 对话页 | 对话气泡 + 建议标签 + 输入框 + 清空按钮 |
| 技能匹配页 | 左侧技能标签云（硬/软分类） + 右侧匹配结果（含雷达图） |
| 登录/注册弹窗 | 模态窗口，切换登录/注册表单 |

**技术细节**：
- ECharts 5.5 CDN 引入，用于雷达图可视化
- JWT 令牌存储在 `localStorage` 中
- 登录状态全局管理（顶部显示用户信息 + 退出按钮）
- 自适应布局，支持移动端

---

## 七、环境要求

| 组件 | 要求 | 用途 |
|------|------|------|
| Python | 3.12+ | 运行环境 |
| MySQL | 5.7+ | 数据库（`career_platform`） |
| DeepSeek API | 有效 Key | AI 对话功能 |
| 浏览器 | 现代浏览器 | 前端页面（推荐 Chrome） |

---

## 八、快速启动步骤

### 步骤 1：克隆/打开项目

```bash
# 使用 IDE（推荐 PyCharm / VS Code）打开项目目录
C:\Users\王淑涵\Desktop\计算机案例模拟\career-platform
```

### 步骤 2：安装 Python 依赖

```bash
cd backend
pip install -r requirements.txt
```

### 步骤 3：准备 MySQL 数据库

**方式一：使用 SQL 脚本（推荐）**

```bash
mysql -u root -p1234 < sql/init.sql
```

**方式二：自动初始化**

启动后端服务后，首次启动会自动建表和插入种子数据（`database.py` 中的 `init_database`）。

### 步骤 4：配置 DeepSeek API Key

编辑 `backend/config.py`，确认 API Key 已配置：

```python
DEEPSEEK_API_KEY = "sk-c5fc1afbe97f4d42b794aab80a5f47f9"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
```

> 如需使用自己的 Key，替换上述值即可。DeepSeek API 申请地址：https://platform.deepseek.com

### 步骤 5：启动后端服务

```bash
cd backend
python main.py
```

或使用 uvicorn 直接启动：

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

启动后终端会显示：
```
==================================================
  职引未来 - AI职业规划平台 v1.0.0
==================================================
  [数据库] MySQL连接池已创建
  [数据库] 初始化完成
  服务已启动: http://localhost:8000
  API文档:    http://localhost:8000/docs
==================================================
```

### 步骤 6：访问应用

在浏览器中打开：**http://localhost:8000**

- 前端页面自动加载
- API 在线文档：**http://localhost:8000/docs**（Swagger UI）

---

## 九、API 接口速查

### 9.1 认证接口（无需登录）

| 路径 | 方法 | 功能 | 请求体 |
|------|------|------|--------|
| `/api/auth/register` | POST | 用户注册 | `{username, password, email?}` |
| `/api/auth/login` | POST | 用户登录 | `{username, password}` |
| `/api/auth/me` | GET | 获取当前用户 | Header: `Authorization: Bearer <token>` |

### 9.2 AI 对话（需登录）

| 路径 | 方法 | 功能 | 请求体 |
|------|------|------|--------|
| `/api/chat` | POST | AI 对话 | `{message, history?}` |
| `/api/chat/history` | GET | 获取对话历史 | — |
| `/api/chat/history` | DELETE | 清空对话历史 | — |

### 9.3 技能匹配（需登录）

| 路径 | 方法 | 功能 | 请求体 |
|------|------|------|--------|
| `/api/match` | POST | 技能-岗位匹配 | `{skill_ids: [1, 2, 3]}` |

### 9.4 数据查询（无需登录）

| 路径 | 方法 | 功能 | 返回 |
|------|------|------|------|
| `/api/skills` | GET | 获取全部技能 | `{success, data: [{id, name, category}], total}` |
| `/api/jobs` | GET | 获取全部岗位 | `{success, data: [{...}], total}` |

---

## 十、技能匹配算法详解

### 加权 Jaccard 相似度

这是技能匹配的核心算法，将硬技能和软技能分别计算后加权求和：

**硬技能**（如 Python、Java、SQL）权重：**70%**
**软技能**（如沟通表达、团队协作）权重：**30%**

```
硬技能匹配度 = (用户拥有的硬技能重要度之和) / (岗位要求全部硬技能重要度之和)
软技能匹配度 = (用户拥有的软技能重要度之和) / (岗位要求全部软技能重要度之和)

最终匹配度 = 硬技能匹配度 × 70 + 软技能匹配度 × 30
```

**技能重要度**：1-5 分，5 = 必备技能（如 Python 对 AI 算法工程师）

### 雷达图

每个匹配结果附带雷达图数据，直观展示用户技能与岗位要求的差距。取岗位最重要的 6 项技能，对比用户掌握情况。

---

## 十一、爬虫系统使用

### 一键运行

```bash
cd backend/scraper
python run_all.py
```

该脚本会：
1. 爬取实习僧（12 个关键词）
2. 爬取 Boss 直聘（12 个关键词）
3. 如果爬虫失败（反爬/网络问题），自动使用内置的 20 条备用数据
4. 将所有数据导入 MySQL `jobs` 和 `job_skills` 表

### 单独运行爬虫

```bash
# 仅爬取实习僧
python backend/scraper/shixiseng.py

# 仅爬取 Boss 直聘
python backend/scraper/boss.py

# 仅导入 JSON 数据到 MySQL
python backend/scraper/import_to_db.py
```

### 爬虫数据缓存

爬取结果自动保存到 `data/` 目录：
- `shixiseng_jobs.json` — 实习僧数据
- `boss_jobs.json` — Boss 直聘数据
- `fallback_jobs.json` — 备用数据

---

## 十二、配置文件说明

### config.py 核心配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | sk-c5fc...（需自行申请） |
| `DEEPSEEK_BASE_URL` | API 地址 | https://api.deepseek.com/v1 |
| `DEEPSEEK_MODEL` | 使用的模型 | deepseek-chat |
| `DB_HOST` | MySQL 地址 | localhost |
| `DB_PORT` | MySQL 端口 | 3306 |
| `DB_USER` | MySQL 用户名 | root |
| `DB_PASSWORD` | MySQL 密码 | 1234 |
| `DB_NAME` | 数据库名 | career_platform |
| `JWT_SECRET` | JWT 签名密钥 | zhiyin-weilai-jwt-secret-key-2024 |
| `JWT_ALGORITHM` | JWT 算法 | HS256 |
| `JWT_EXPIRE_HOURS` | Token 有效期 | 24 小时 |
| `CORS_ORIGINS` | 允许跨域来源 | ["*"] |
| `MAX_CHAT_HISTORY` | 保留最近对话轮数 | 20 |
| `SYSTEM_PROMPT` | AI 系统角色设定 | 资深职业规划师 |

---

## 十三、开发规范

1. **异步编程**：使用 `async/await` 异步处理数据库查询和 HTTP 请求
2. **数据库连接池**：使用 `aiomysql.create_pool` 管理连接，避免频繁创建/销毁连接
3. **密码安全**：bcrypt 哈希加密，不存储明文密码
4. **JWT 认证**：请求头格式 `Authorization: Bearer <token>`，24 小时过期
5. **Pydantic 验证**：所有 API 参数使用 Pydantic 模型进行类型校验和约束
6. **统一响应格式**：`{success: bool, message: str, data: ...}`
7. **前端资源服务**：FastAPI 挂载前端静态文件，`/` 路由返回 `index.html`
8. **幂等初始化**：数据库建表和种子数据使用 `IF NOT EXISTS` / 计数检查，重复启动不报错

---

## 十四、常见问题

**Q1: DeepSeek API 调用失败怎么办？**
> 检查 `config.py` 中的 `DEEPSEEK_API_KEY` 是否有效。可在 https://platform.deepseek.com 注册获取 API Key。

**Q2: 数据库连接失败？**
> 确认 MySQL 已启动，用户 root 密码为 `1234`，数据库 `career_platform` 已创建。也可通过 `sql/init.sql` 一键初始化。

**Q3: 如何替换前端页面？**
> 修改 `frontend/index.html`、`frontend/css/style.css` 和 `frontend/js/` 下的 JS 文件即可。FastAPI 会自动挂载静态文件服务。

**Q4: 爬虫数据如何更新？**
> 运行 `python backend/scraper/run_all.py`，爬虫会自动获取最新数据并导入数据库。

**Q5: AI 回复太长或太短怎么调整？**
> 修改 `backend/services/llm_service.py` 中的 `max_tokens`（最大长度）和 `temperature`（创造性，0.7 为适中有创造性）。

**Q6: 前端路由路径和 API 冲突怎么办？**
> 前端路由注册在 API 路由之后（`main.py` 中），API 路由优先级更高。

**Q7: 如何部署到生产环境？**
> 使用 Gunicorn + Uvicorn workers：
> ```bash
> pip install gunicorn
> gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
> ```

---

## 十五、扩展功能建议

- **简历上传与分析**：支持 PDF/Word 简历上传，AI 自动提取技能标签
- **学习路径推荐**：根据目标岗位，推荐在线课程和学习资源
- **模拟面试**：AI 扮演面试官，进行模拟面试练习
- **社区功能**：学生交流经验、分享面经
- **企业对接**：对接企业招聘系统，实现一键投递

---

日期：2026年7月1日

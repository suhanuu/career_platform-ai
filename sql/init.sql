
-- 1. 建库
CREATE DATABASE IF NOT EXISTS career_platform
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE career_platform;

-- 2. 建表
-- 技能表
CREATE TABLE IF NOT EXISTS skills (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(50)  NOT NULL COMMENT '技能名称',
    category    VARCHAR(20)  NOT NULL COMMENT '技能类别: hard/soft',
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_skills_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 岗位表
CREATE TABLE IF NOT EXISTS jobs (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    title       VARCHAR(100) NOT NULL COMMENT '岗位名称',
    description TEXT         NOT NULL COMMENT '岗位描述',
    industry    VARCHAR(50)  NOT NULL COMMENT '所属行业',
    salary_min  INT          NOT NULL COMMENT '最低月薪(千元)',
    salary_max  INT          NOT NULL COMMENT '最高月薪(千元)',
    education   VARCHAR(20)  NOT NULL COMMENT '学历要求',
    experience  VARCHAR(20)  NOT NULL COMMENT '经验要求',
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_jobs_industry (industry)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 岗位-技能关联表
CREATE TABLE IF NOT EXISTS job_skills (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    job_id      INT      NOT NULL COMMENT '岗位ID',
    skill_id    INT      NOT NULL COMMENT '技能ID',
    importance  TINYINT  NOT NULL DEFAULT 3 COMMENT '重要度1-5 (5=必备)',
    UNIQUE INDEX uq_job_skill (job_id, skill_id),
    CONSTRAINT fk_jobskills_job   FOREIGN KEY (job_id)   REFERENCES jobs(id)   ON DELETE CASCADE,
    CONSTRAINT fk_jobskills_skill FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 3. 种子数据
-- ============================================

-- 硬技能 (15个)
INSERT INTO skills (name, category) VALUES
('Python',        'hard'),
('Java',          'hard'),
('JavaScript',    'hard'),
('SQL',           'hard'),
('数据分析',      'hard'),
('机器学习',      'hard'),
('Linux',         'hard'),
('Docker',        'hard'),
('Git',           'hard'),
('Excel',         'hard'),
('产品设计',      'hard'),
('项目管理',      'hard'),
('市场营销',      'hard'),
('UI设计',        'hard'),
('C++',           'hard');

-- 软技能 (15个)
INSERT INTO skills (name, category) VALUES
('沟通表达',      'soft'),
('团队协作',      'soft'),
('逻辑思维',      'soft'),
('时间管理',      'soft'),
('领导力',        'soft'),
('抗压能力',      'soft'),
('学习能力',      'soft'),
('创新能力',      'soft'),
('英语能力',      'soft'),
('文档写作',      'soft'),
('问题解决',      'soft'),
('数据分析思维',  'soft'),
('执行力',        'soft'),
('客户服务意识',  'soft'),
('演讲展示',      'soft');

-- ============================================
-- 岗位数据 (15个, 覆盖5个行业)
-- ============================================
INSERT INTO jobs (title, description, industry, salary_min, salary_max, education, experience) VALUES
-- 互联网/IT (5个)
('Python后端开发工程师', '负责公司核心业务系统的后端开发与维护，参与系统架构设计，编写高质量代码，保障系统稳定性和性能。', '互联网/IT', 12, 25, '本科', '应届生'),
('前端开发工程师',       '负责Web前端页面的开发与优化，与设计师和后端工程师紧密配合，实现优秀的用户体验。',     '互联网/IT', 10, 22, '本科', '应届生'),
('数据分析师',           '负责业务数据的提取、分析和可视化，为产品和运营决策提供数据支持，撰写数据分析报告。',     '互联网/IT', 10, 20, '本科', '应届生'),
('AI算法工程师',         '参与机器学习模型的训练与部署，负责算法优化和效果评估，跟踪前沿技术发展。',               '互联网/IT', 18, 35, '硕士', '应届生'),
('产品经理',             '负责产品需求分析、功能设计和项目推进，协调研发、设计和运营团队，确保产品按时交付。',     '互联网/IT', 12, 24, '本科', '应届生'),

-- 金融 (3个)
('金融分析师',           '负责行业研究和公司基本面分析，撰写研究报告，为投资决策提供专业建议。',                   '金融', 10, 20, '本科', '应届生'),
('风险管理专员',         '负责信用风险和市场风险的识别与监控，建立风险评估模型，制定风险控制策略。',               '金融', 12, 22, '本科', '应届生'),
('量化交易研究员',       '开发量化交易策略，进行回测和模拟交易，优化交易模型的表现。',                             '金融', 18, 40, '硕士', '应届生'),

-- 制造业 (2个)
('智能制造工程师',       '负责生产线的自动化和智能化改造，参与工业机器人的部署和维护，优化生产流程。',             '制造业', 10, 18, '本科', '应届生'),
('质量管理工程师',       '制定和执行质量控制标准，分析质量数据，推动产品质量的持续改进。',                       '制造业', 8, 15, '本科', '应届生'),

-- 教育/咨询 (3个)
('管理咨询顾问',         '为客户企业提供战略规划和运营优化咨询，进行市场调研和数据分析，撰写咨询报告。',           '教育/咨询', 12, 25, '本科', '应届生'),
('职业规划师',           '为学生和职场人士提供职业发展指导，制定个人发展计划，组织职业规划讲座和活动。',           '教育/咨询', 8, 15, '本科', '应届生'),
('培训讲师',             '设计和讲授专业课程，评估培训效果，不断优化课程内容和教学方式。',                       '教育/咨询', 8, 16, '本科', '应届生'),

-- 电商/新媒体 (2个)
('新媒体运营',           '负责公司社交媒体账号的内容策划和运营，提升粉丝活跃度和品牌影响力，分析运营数据。',       '电商/新媒体', 8, 15, '本科', '应届生'),
('电商运营专员',         '负责电商平台店铺的日常运营，策划促销活动，分析销售数据，提升店铺转化率。',             '电商/新媒体', 8, 14, '本科', '应届生');

-- ============================================
-- 岗位-技能关联 (每个岗位5-8个技能)
-- ============================================

-- Python后端开发工程师 (job_id=1)
INSERT INTO job_skills (job_id, skill_id, importance) VALUES
(1, 1, 5),   -- Python      必备
(1, 3, 4),   -- JavaScript  重要
(1, 4, 5),   -- SQL         必备
(1, 7, 4),   -- Linux       重要
(1, 8, 3),   -- Docker      加分
(1, 9, 4),   -- Git         重要
(1, 16, 3),  -- 沟通表达    加分
(1, 18, 4),  -- 逻辑思维    重要
(1, 22, 3);  -- 学习能力    加分

-- 前端开发工程师 (job_id=2)
INSERT INTO job_skills (job_id, skill_id, importance) VALUES
(2, 3, 5),   -- JavaScript  必备
(2, 14, 4),  -- UI设计       重要
(2, 9, 3),   -- Git         加分
(2, 16, 3),  -- 沟通表达    加分
(2, 17, 4),  -- 团队协作    重要
(2, 18, 3),  -- 逻辑思维    重要
(2, 22, 4);  -- 学习能力    重要

-- 数据分析师 (job_id=3)
INSERT INTO job_skills (job_id, skill_id, importance) VALUES
(3, 1, 4),   -- Python      重要
(3, 4, 5),   -- SQL         必备
(3, 5, 5),   -- 数据分析    必备
(3, 10, 4),  -- Excel       重要
(3, 6, 3),   -- 机器学习    加分
(3, 18, 4),  -- 逻辑思维    重要
(3, 22, 3),  -- 学习能力    加分
(3, 27, 4);  -- 数据分析思维 重要

-- AI算法工程师 (job_id=4)
INSERT INTO job_skills (job_id, skill_id, importance) VALUES
(4, 1, 5),   -- Python      必备
(4, 6, 5),   -- 机器学习    必备
(4, 4, 4),   -- SQL         重要
(4, 15, 3),  -- C++         加分
(4, 18, 5),  -- 逻辑思维    必备
(4, 22, 4),  -- 学习能力    重要
(4, 25, 3);  -- 创新能力    加分

-- 产品经理 (job_id=5)
INSERT INTO job_skills (job_id, skill_id, importance) VALUES
(5, 12, 4),  -- 项目管理    重要
(5, 11, 3),  -- 产品设计    加分
(5, 16, 5),  -- 沟通表达    必备
(5, 17, 4),  -- 团队协作    重要
(5, 18, 4),  -- 逻辑思维    重要
(5, 25, 3),  -- 创新能力    加分
(5, 26, 4);  -- 文档写作    重要

-- 金融分析师 (job_id=6)
INSERT INTO job_skills (job_id, skill_id, importance) VALUES
(6, 10, 5),  -- Excel       必备
(6, 5, 4),   -- 数据分析    重要
(6, 4, 3),   -- SQL         加分
(6, 16, 4),  -- 沟通表达    重要
(6, 18, 5),  -- 逻辑思维    必备
(6, 19, 3),  -- 时间管理    加分
(6, 26, 4);  -- 文档写作    重要

-- 风险管理专员 (job_id=7)
INSERT INTO job_skills (job_id, skill_id, importance) VALUES
(7, 10, 4),  -- Excel       重要
(7, 5, 4),   -- 数据分析    重要
(7, 4, 3),   -- SQL         加分
(7, 1, 3),   -- Python      加分
(7, 18, 5),  -- 逻辑思维    必备
(7, 26, 4),  -- 文档写作    重要
(7, 27, 4);  -- 数据分析思维 重要

-- 量化交易研究员 (job_id=8)
INSERT INTO job_skills (job_id, skill_id, importance) VALUES
(8, 1, 5),   -- Python      必备
(8, 4, 4),   -- SQL         重要
(8, 5, 5),   -- 数据分析    必备
(8, 6, 4),   -- 机器学习    重要
(8, 15, 3),  -- C++         加分
(8, 18, 5),  -- 逻辑思维    必备
(8, 21, 3);  -- 抗压能力    加分

-- 智能制造工程师 (job_id=9)
INSERT INTO job_skills (job_id, skill_id, importance) VALUES
(9, 1, 4),   -- Python      重要
(9, 2, 3),   -- Java        加分
(9, 7, 4),   -- Linux       重要
(9, 4, 3),   -- SQL         加分
(9, 17, 4),  -- 团队协作    重要
(9, 18, 3),  -- 逻辑思维    重要
(9, 22, 3);  -- 学习能力    加分

-- 质量管理工程师 (job_id=10)
INSERT INTO job_skills (job_id, skill_id, importance) VALUES
(10, 5, 3),  -- 数据分析    加分
(10, 10, 4), -- Excel       重要
(10, 17, 3), -- 团队协作    加分
(10, 18, 4), -- 逻辑思维    重要
(10, 28, 4), -- 执行力      重要
(10, 26, 3), -- 文档写作    加分
(10, 27, 3); -- 数据分析思维 加分

-- 管理咨询顾问 (job_id=11)
INSERT INTO job_skills (job_id, skill_id, importance) VALUES
(11, 5, 4),  -- 数据分析    重要
(11, 10, 4), -- Excel       重要
(11, 16, 5), -- 沟通表达    必备
(11, 17, 3), -- 团队协作    重要
(11, 18, 5), -- 逻辑思维    必备
(11, 25, 3), -- 创新能力    加分
(11, 26, 4), -- 文档写作    重要
(11, 30, 4); -- 演讲展示    重要

-- 职业规划师 (job_id=12)
INSERT INTO job_skills (job_id, skill_id, importance) VALUES
(12, 16, 5), -- 沟通表达    必备
(12, 17, 3), -- 团队协作    加分
(12, 22, 4), -- 学习能力    重要
(12, 25, 3), -- 创新能力    加分
(12, 26, 3), -- 文档写作    加分
(12, 29, 4), -- 客户服务意识 重要
(12, 30, 3); -- 演讲展示    加分

-- 培训讲师 (job_id=13)
INSERT INTO job_skills (job_id, skill_id, importance) VALUES
(13, 16, 5), -- 沟通表达    必备
(13, 17, 3), -- 团队协作    加分
(13, 22, 4), -- 学习能力    重要
(13, 26, 3), -- 文档写作    重要
(13, 30, 5), -- 演讲展示    必备
(13, 19, 3); -- 时间管理    加分

-- 新媒体运营 (job_id=14)
INSERT INTO job_skills (job_id, skill_id, importance) VALUES
(14, 13, 3), -- 市场营销    加分
(14, 5, 3),  -- 数据分析    重要
(14, 16, 4), -- 沟通表达    重要
(14, 25, 5), -- 创新能力    必备
(14, 26, 4), -- 文档写作    重要
(14, 22, 3), -- 学习能力    加分
(14, 29, 3); -- 客户服务意识 加分

-- 电商运营专员 (job_id=15)
INSERT INTO job_skills (job_id, skill_id, importance) VALUES
(15, 13, 4), -- 市场营销    重要
(15, 10, 4), -- Excel       重要
(15, 5, 4),  -- 数据分析    重要
(15, 16, 3), -- 沟通表达    加分
(15, 25, 3), -- 创新能力    加分
(15, 28, 4), -- 执行力      重要
(15, 29, 4); -- 客户服务意识 重要

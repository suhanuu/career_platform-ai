"""
「职引未来」数据库管理
包含: MySQL连接池 + 建表 + 种子数据初始化
"""
import aiomysql
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DB_CHARSET
from config import DB_POOL_MIN_SIZE, DB_POOL_MAX_SIZE

# 全局连接池 (FastAPI启动时创建)
pool = None


async def create_pool():
    """创建MySQL连接池 (FastAPI启动时调用)"""
    global pool
    pool = await aiomysql.create_pool(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB_NAME,
        charset=DB_CHARSET,
        minsize=DB_POOL_MIN_SIZE,
        maxsize=DB_POOL_MAX_SIZE,
        autocommit=True,
    )
    print(f"[数据库] MySQL连接池已创建 (min={DB_POOL_MIN_SIZE}, max={DB_POOL_MAX_SIZE})")
    return pool


async def close_pool():
    """关闭连接池 (FastAPI关闭时调用)"""
    global pool
    if pool:
        pool.close()
        await pool.wait_closed()
        print("[数据库] MySQL连接池已关闭")


async def get_pool():
    """获取连接池实例"""
    global pool
    if pool is None:
        pool = await create_pool()
    return pool


async def init_database():
    """
    初始化数据库: 建表 + 插入种子数据
    使用 IF NOT EXISTS 保证幂等性 (重复执行不报错)
    """
    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # ---- 建表 ----
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS skills (
                    id          INT AUTO_INCREMENT PRIMARY KEY,
                    name        VARCHAR(50)  NOT NULL,
                    category    VARCHAR(20)  NOT NULL,
                    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_skills_category (category)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            await cur.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id          INT AUTO_INCREMENT PRIMARY KEY,
                    title       VARCHAR(100) NOT NULL,
                    description TEXT         NOT NULL,
                    industry    VARCHAR(50)  NOT NULL,
                    salary_min  INT          NOT NULL,
                    salary_max  INT          NOT NULL,
                    education   VARCHAR(20)  NOT NULL,
                    experience  VARCHAR(20)  NOT NULL,
                    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_jobs_industry (industry)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            await cur.execute("""
                CREATE TABLE IF NOT EXISTS job_skills (
                    id          INT AUTO_INCREMENT PRIMARY KEY,
                    job_id      INT      NOT NULL,
                    skill_id    INT      NOT NULL,
                    importance  TINYINT  NOT NULL DEFAULT 3,
                    UNIQUE INDEX uq_job_skill (job_id, skill_id),
                    CONSTRAINT fk_jobskills_job   FOREIGN KEY (job_id)   REFERENCES jobs(id)   ON DELETE CASCADE,
                    CONSTRAINT fk_jobskills_skill FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            await cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id            INT AUTO_INCREMENT PRIMARY KEY,
                    username      VARCHAR(50)  NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    email         VARCHAR(100) NOT NULL DEFAULT '',
                    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            await cur.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id          INT AUTO_INCREMENT PRIMARY KEY,
                    user_id     INT          NOT NULL,
                    role        VARCHAR(10)  NOT NULL COMMENT 'user/assistant',
                    content     TEXT         NOT NULL,
                    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_user_time (user_id, created_at),
                    CONSTRAINT fk_chat_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # ---- 检查是否已有种子数据 ----
            await cur.execute("SELECT COUNT(*) FROM skills")
            count = (await cur.fetchone())[0]

            if count == 0:
                print("[数据库] 首次启动，插入种子数据...")
                await _insert_seed_data(cur)
                print("[数据库] 种子数据已插入 (30技能 + 15岗位 + 107技能关联)")
            else:
                print(f"[数据库] 数据已存在 (技能{count}个)，跳过种子数据插入")

    print("[数据库] 初始化完成")


async def _insert_seed_data(cur):
    """插入种子数据 (仅在空库时执行)"""

    # 硬技能 (15个)
    await cur.execute("""
        INSERT INTO skills (name, category) VALUES
        ('Python', 'hard'), ('Java', 'hard'), ('JavaScript', 'hard'),
        ('SQL', 'hard'), ('数据分析', 'hard'), ('机器学习', 'hard'),
        ('Linux', 'hard'), ('Docker', 'hard'), ('Git', 'hard'),
        ('Excel', 'hard'), ('产品设计', 'hard'), ('项目管理', 'hard'),
        ('市场营销', 'hard'), ('UI设计', 'hard'), ('C++', 'hard')
    """)

    # 软技能 (15个)
    await cur.execute("""
        INSERT INTO skills (name, category) VALUES
        ('沟通表达', 'soft'), ('团队协作', 'soft'), ('逻辑思维', 'soft'),
        ('时间管理', 'soft'), ('领导力', 'soft'), ('抗压能力', 'soft'),
        ('学习能力', 'soft'), ('创新能力', 'soft'), ('英语能力', 'soft'),
        ('文档写作', 'soft'), ('问题解决', 'soft'), ('数据分析思维', 'soft'),
        ('执行力', 'soft'), ('客户服务意识', 'soft'), ('演讲展示', 'soft')
    """)

    # 岗位 (15个)
    await cur.execute("""
        INSERT INTO jobs (title, description, industry, salary_min, salary_max, education, experience) VALUES
        ('Python后端开发工程师', '负责公司核心业务系统的后端开发与维护，参与系统架构设计，编写高质量代码，保障系统稳定性和性能。', '互联网/IT', 12, 25, '本科', '应届生'),
        ('前端开发工程师', '负责Web前端页面的开发与优化，与设计师和后端工程师紧密配合，实现优秀的用户体验。', '互联网/IT', 10, 22, '本科', '应届生'),
        ('数据分析师', '负责业务数据的提取、分析和可视化，为产品和运营决策提供数据支持，撰写数据分析报告。', '互联网/IT', 10, 20, '本科', '应届生'),
        ('AI算法工程师', '参与机器学习模型的训练与部署，负责算法优化和效果评估，跟踪前沿技术发展。', '互联网/IT', 18, 35, '硕士', '应届生'),
        ('产品经理', '负责产品需求分析、功能设计和项目推进，协调研发、设计和运营团队，确保产品按时交付。', '互联网/IT', 12, 24, '本科', '应届生'),
        ('金融分析师', '负责行业研究和公司基本面分析，撰写研究报告，为投资决策提供专业建议。', '金融', 10, 20, '本科', '应届生'),
        ('风险管理专员', '负责信用风险和市场风险的识别与监控，建立风险评估模型，制定风险控制策略。', '金融', 12, 22, '本科', '应届生'),
        ('量化交易研究员', '开发量化交易策略，进行回测和模拟交易，优化交易模型的表现。', '金融', 18, 40, '硕士', '应届生'),
        ('智能制造工程师', '负责生产线的自动化和智能化改造，参与工业机器人的部署和维护，优化生产流程。', '制造业', 10, 18, '本科', '应届生'),
        ('质量管理工程师', '制定和执行质量控制标准，分析质量数据，推动产品质量的持续改进。', '制造业', 8, 15, '本科', '应届生'),
        ('管理咨询顾问', '为客户企业提供战略规划和运营优化咨询，进行市场调研和数据分析，撰写咨询报告。', '教育/咨询', 12, 25, '本科', '应届生'),
        ('职业规划师', '为学生和职场人士提供职业发展指导，制定个人发展计划，组织职业规划讲座和活动。', '教育/咨询', 8, 15, '本科', '应届生'),
        ('培训讲师', '设计和讲授专业课程，评估培训效果，不断优化课程内容和教学方式。', '教育/咨询', 8, 16, '本科', '应届生'),
        ('新媒体运营', '负责公司社交媒体账号的内容策划和运营，提升粉丝活跃度和品牌影响力，分析运营数据。', '电商/新媒体', 8, 15, '本科', '应届生'),
        ('电商运营专员', '负责电商平台店铺的日常运营，策划促销活动，分析销售数据，提升店铺转化率。', '电商/新媒体', 8, 14, '本科', '应届生')
    """)

    # 岗位-技能关联 (107条)
    job_skill_data = [
        # (job_id, skill_id, importance)
        # Python后端开发工程师
        (1, 1, 5), (1, 3, 4), (1, 4, 5), (1, 7, 4), (1, 8, 3), (1, 9, 4),
        (1, 16, 3), (1, 18, 4), (1, 22, 3),
        # 前端开发工程师
        (2, 3, 5), (2, 14, 4), (2, 9, 3), (2, 16, 3), (2, 17, 4), (2, 18, 3), (2, 22, 4),
        # 数据分析师
        (3, 1, 4), (3, 4, 5), (3, 5, 5), (3, 10, 4), (3, 6, 3), (3, 18, 4), (3, 22, 3), (3, 27, 4),
        # AI算法工程师
        (4, 1, 5), (4, 6, 5), (4, 4, 4), (4, 15, 3), (4, 18, 5), (4, 22, 4), (4, 25, 3),
        # 产品经理
        (5, 12, 4), (5, 11, 3), (5, 16, 5), (5, 17, 4), (5, 18, 4), (5, 25, 3), (5, 26, 4),
        # 金融分析师
        (6, 10, 5), (6, 5, 4), (6, 4, 3), (6, 16, 4), (6, 18, 5), (6, 19, 3), (6, 26, 4),
        # 风险管理专员
        (7, 10, 4), (7, 5, 4), (7, 4, 3), (7, 1, 3), (7, 18, 5), (7, 26, 4), (7, 27, 4),
        # 量化交易研究员
        (8, 1, 5), (8, 4, 4), (8, 5, 5), (8, 6, 4), (8, 15, 3), (8, 18, 5), (8, 21, 3),
        # 智能制造工程师
        (9, 1, 4), (9, 2, 3), (9, 7, 4), (9, 4, 3), (9, 17, 4), (9, 18, 3), (9, 22, 3),
        # 质量管理工程师
        (10, 5, 3), (10, 10, 4), (10, 17, 3), (10, 18, 4), (10, 28, 4), (10, 26, 3), (10, 27, 3),
        # 管理咨询顾问
        (11, 5, 4), (11, 10, 4), (11, 16, 5), (11, 17, 3), (11, 18, 5), (11, 25, 3), (11, 26, 4), (11, 30, 4),
        # 职业规划师
        (12, 16, 5), (12, 17, 3), (12, 22, 4), (12, 25, 3), (12, 26, 3), (12, 29, 4), (12, 30, 3),
        # 培训讲师
        (13, 16, 5), (13, 17, 3), (13, 22, 4), (13, 26, 3), (13, 30, 5), (13, 19, 3),
        # 新媒体运营
        (14, 13, 3), (14, 5, 3), (14, 16, 4), (14, 25, 5), (14, 26, 4), (14, 22, 3), (14, 29, 3),
        # 电商运营专员
        (15, 13, 4), (15, 10, 4), (15, 5, 4), (15, 16, 3), (15, 25, 3), (15, 28, 4), (15, 29, 4),
    ]
    for job_id, skill_id, importance in job_skill_data:
        await cur.execute(
            "INSERT INTO job_skills (job_id, skill_id, importance) VALUES (%s, %s, %s)",
            (job_id, skill_id, importance)
        )

"""
「职引未来」配置文件
包含: MySQL连接 + DeepSeek API + 应用设置
"""

# ========== DeepSeek API 配置 ==========
DEEPSEEK_API_KEY = "sk-c5fc1afbe97f4d42b794aab80a5f47f9"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL = "deepseek-chat"  # 性价比最高, 如需更强推理可换 deepseek-reasoner

# ========== MySQL 数据库配置 ==========
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "1234"
DB_NAME = "career_platform"
DB_CHARSET = "utf8mb4"

# 数据库连接池配置
DB_POOL_MIN_SIZE = 2
DB_POOL_MAX_SIZE = 10

# ========== JWT 认证配置 ==========
JWT_SECRET = "zhiyin-weilai-jwt-secret-key-2024"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24

# ========== 应用配置 ==========
APP_TITLE = "职引未来 - AI职业规划平台"
APP_VERSION = "1.0.0"
CORS_ORIGINS = ["*"]  # 本地开发允许所有来源

# ========== AI对话配置 ==========
MAX_CHAT_HISTORY = 20  # 保留最近N轮对话
SYSTEM_PROMPT = """你是一位资深的职业规划师，拥有10年以上的高校就业指导经验。
你的职责是：
1. 根据学生的专业、年级、兴趣，提供个性化的职业发展方向建议
2. 帮助学生了解不同行业和岗位的真实情况
3. 给出技能提升、实习、证书等具体的行动计划
4. 用温暖、鼓励的语气交流，但建议要专业、具体、可落地

请注意：
- 优先推荐与用户专业对口的岗位，同时提供跨界发展的可能性
- 回答要包含具体的岗位名称、薪资范围、所需技能
- 如果用户信息不足，主动询问关键信息（专业、年级、兴趣方向等）
- 每次对话结束时，给对方一个小行动建议"""

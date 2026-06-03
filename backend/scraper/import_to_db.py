"""
爬取数据导入MySQL
读取爬虫JSON → 匹配技能标签 → 写入 jobs + job_skills 表
"""
import asyncio
import json
import sys
from pathlib import Path

# 项目根目录加入路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import aiomysql
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DB_CHARSET

# 技能关键词映射表（从岗位名称/描述中匹配）
SKILL_KEYWORDS = {
    "Python": ["python"],
    "Java": ["java"],
    "JavaScript": ["javascript", "js", "前端", "vue", "react", "web"],
    "SQL": ["sql", "数据库", "mysql", "oracle"],
    "数据分析": ["数据分析", "数据挖掘", "数据", "excel", "tableau"],
    "机器学习": ["机器学习", "深度学习", "ai", "算法", "tensorflow", "pytorch", "nlp"],
    "Linux": ["linux", "unix", "shell"],
    "Docker": ["docker", "k8s", "kubernetes", "容器"],
    "Git": ["git", "svn", "版本控制"],
    "C++": ["c++", "cpp", "c语言"],
    "产品设计": ["产品", "axure", "sketch", "产品经理", "prd"],
    "项目管理": ["项目管理", "scrum", "agile", "敏捷"],
    "市场营销": ["营销", "市场", "推广", "新媒体", "短视频", "直播"],
    "UI设计": ["ui", "ue", "设计", "figma", "ps", "illustrator"],
    "Excel": ["excel", "office", "wps"],
    "沟通表达": ["沟通", "表达"],
    "团队协作": ["团队", "协作", "合作"],
    "逻辑思维": ["逻辑", "思维", "分析"],
    "抗压能力": ["抗压", "承压", "压力"],
    "学习能力": ["学习", "自学"],
    "创新能力": ["创新", "创意", "创造"],
    "文档写作": ["文档", "方案", "写作"],
    "执行力": ["执行", "落地"],
    "客户服务意识": ["客户", "服务", "沟通能力"],
    "英语能力": ["英语", "英文", "cet-6", "cet-4"],
}


async def import_jobs(json_file: str):
    """将爬取的JSON数据导入MySQL"""
    with open(json_file, "r", encoding="utf-8") as f:
        jobs_data = json.load(f)

    pool = await aiomysql.create_pool(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD,
        db=DB_NAME, charset=DB_CHARSET, minsize=1, maxsize=3, autocommit=True,
    )

    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            # 加载技能ID映射
            await cur.execute("SELECT id, name FROM skills")
            skill_rows = await cur.fetchall()
            skill_map = {row["name"]: row["id"] for row in skill_rows}

            inserted = 0
            for job in jobs_data:
                # 检查是否已存在
                await cur.execute(
                    "SELECT id FROM jobs WHERE title = %s LIMIT 1", (job["title"],)
                )
                if await cur.fetchone():
                    continue

                # 插入岗位
                await cur.execute(
                    """INSERT INTO jobs (title, description, industry, salary_min, salary_max, education, experience)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (
                        job["title"],
                        job.get("description", ""),
                        job.get("industry", "互联网/IT"),
                        job.get("salary_min", 6),
                        job.get("salary_max", 15),
                        job.get("education", "本科"),
                        job.get("experience", "应届生"),
                    ),
                )
                job_id = cur.lastrowid

                # 技能匹配（从标题+描述中提取）
                desc_lower = (job.get("description", "") + job.get("title", "")).lower()
                skill_links = []
                for skill_name, keywords in SKILL_KEYWORDS.items():
                    if any(kw in desc_lower for kw in keywords):
                        skill_id = skill_map.get(skill_name)
                        if skill_id:
                            # 计算重要度（标题中出现 = 高权）
                            importance = 5 if any(kw in job["title"].lower() for kw in keywords) else 3
                            skill_links.append((job_id, skill_id, importance))

                # 插入技能关联（最多8个）
                for link in skill_links[:8]:
                    await cur.execute(
                        "INSERT IGNORE INTO job_skills (job_id, skill_id, importance) VALUES (%s, %s, %s)",
                        link,
                    )

                inserted += 1

            print(f"[导入] {Path(json_file).name} → {inserted} 条新岗位入库")

    pool.close()
    await pool.wait_closed()


async def run_import():
    """导入所有爬虫数据"""
    data_dir = Path(__file__).parent.parent.parent / "data"
    json_files = list(data_dir.glob("*.json"))

    if not json_files:
        print("[导入] 未找到JSON文件，请先运行爬虫脚本")
        return

    for f in json_files:
        await import_jobs(str(f))

    print("[导入] 完成")


if __name__ == "__main__":
    asyncio.run(run_import())

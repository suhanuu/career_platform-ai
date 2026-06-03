"""
============================================
技能-岗位匹配算法
核心: 加权Jaccard相似度 (硬技能权重0.7, 软技能权重0.3)
============================================
"""
from database import get_pool
from models.schemas import MatchResult, SkillGap, JobSkillDetail


async def calculate_match(user_skill_ids: list[int], top_n: int = 5):
    """
    根据用户技能ID列表，计算与所有岗位的匹配度

    算法:
        1. 查出用户技能的分类 (hard/soft)
        2. 查出每个岗位要求的技能及其重要度
        3. 对每个岗位计算加权Jaccard相似度:
           - 交集权重 = Σ(importance of 用户有的技能)
           - 并集权重 = Σ(importance of 岗位全部技能)
           - 匹配度 = 交集权重 / 并集权重 (加权Jaccard)
        4. 按匹配度降序返回Top N

    参数:
        user_skill_ids: 用户选中的技能ID列表
        top_n: 返回前N个匹配岗位

    返回:
        List[MatchResult]
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # ---- 1. 获取用户技能的分类 ----
            if not user_skill_ids:
                return []

            placeholders = ",".join(["%s"] * len(user_skill_ids))
            await cur.execute(
                f"SELECT id, name, category FROM skills WHERE id IN ({placeholders})",
                user_skill_ids,
            )
            user_skills = await cur.fetchall()
            # user_skills: [(id, name, category), ...]

            user_skill_set = {row[0] for row in user_skills}  # 用户技能ID集合

            # ---- 2. 获取每个岗位的全部技能要求 ----
            await cur.execute("""
                SELECT j.id AS job_id, j.title, j.description, j.industry,
                       j.salary_min, j.salary_max, j.education, j.experience,
                       s.id AS skill_id, s.name AS skill_name, s.category,
                       js.importance
                FROM jobs j
                JOIN job_skills js ON j.id = js.job_id
                JOIN skills s ON js.skill_id = s.id
                ORDER BY j.id, js.importance DESC
            """)
            rows = await cur.fetchall()

    # ---- 3. 按岗位分组 ----
    jobs_data = {}  # {job_id: {job_info, skills: [...]}}
    for row in rows:
        job_id = row[0]
        if job_id not in jobs_data:
            jobs_data[job_id] = {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "industry": row[3],
                "salary_min": row[4],
                "salary_max": row[5],
                "education": row[6],
                "experience": row[7],
                "skills": [],
            }
        jobs_data[job_id]["skills"].append({
            "skill_id": row[8],
            "skill_name": row[9],
            "category": row[10],
            "importance": row[11],
        })

    # ---- 4. 计算每个岗位的加权匹配度 ----
    results = []
    for job_id, job in jobs_data.items():
        # 分别统计 hard / soft 的权重
        hard_intersection = 0  # 硬技能交集权重
        hard_union = 0         # 硬技能并集权重
        soft_intersection = 0  # 软技能交集权重
        soft_union = 0         # 软技能并集权重

        skill_gaps = []        # 技能差距分析

        for s in job["skills"]:
            importance = s["importance"]
            user_has = s["skill_id"] in user_skill_set

            skill_gaps.append(SkillGap(
                skill_name=s["skill_name"],
                importance=importance,
                user_has=user_has,
            ))

            if s["category"] == "hard":
                hard_union += importance
                if user_has:
                    hard_intersection += importance
            else:
                soft_union += importance
                if user_has:
                    soft_intersection += importance

        # 加权Jaccard: 硬技能权重0.7, 软技能权重0.3
        hard_rate = (hard_intersection / hard_union * 100) if hard_union > 0 else 0
        soft_rate = (soft_intersection / soft_union * 100) if soft_union > 0 else 0
        match_rate = round(hard_rate * 0.7 + soft_rate * 0.3, 1)

        # ---- 雷达图数据 ----
        # 取前6个最重要的技能做雷达图
        radar_skills = sorted(job["skills"], key=lambda x: x["importance"], reverse=True)[:6]

        results.append(MatchResult(
            job={
                "id": job["id"],
                "title": job["title"],
                "description": job["description"],
                "industry": job["industry"],
                "salary_min": job["salary_min"],
                "salary_max": job["salary_max"],
                "education": job["education"],
                "experience": job["experience"],
                "skills": [
                    JobSkillDetail(
                        skill_id=s["skill_id"],
                        skill_name=s["skill_name"],
                        importance=s["importance"],
                    ) for s in job["skills"]
                ],
            },
            match_rate=match_rate,
            radar_data={
                "labels": [s["skill_name"] for s in radar_skills],
                "user_values": [
                    s["importance"] if s["skill_id"] in user_skill_set else 0
                    for s in radar_skills
                ],
                "job_values": [s["importance"] for s in radar_skills],
            },
            skill_gaps=skill_gaps,
        ))

    # ---- 5. 按匹配度降序排序，取Top N ----
    results.sort(key=lambda x: x.match_rate, reverse=True)
    return results[:top_n]

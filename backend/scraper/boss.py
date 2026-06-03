"""
Boss直聘岗位爬虫
搜索关键词 → 解析岗位列表 → 入库
"""
import asyncio
import httpx
import json
import random
import re
from pathlib import Path

# 浏览器伪装
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://www.zhipin.com/",
}

# Boss直聘搜索 API
SEARCH_URL = "https://www.zhipin.com/wapi/zpgeek/search/joblist.json"

# 城市编码 (全国=100010000)
CITY_CODE = "100010000"

KEYWORDS = [
    "Python", "前端", "数据分析", "Java",
    "产品经理", "UI设计", "新媒体运营", "算法",
    "软件测试", "运维", "市场营销", "人力资源",
]


async def search_jobs(keyword: str, page: int = 1, page_size: int = 30) -> list:
    """搜索Boss直聘岗位"""
    params = {
        "query": keyword,
        "city": CITY_CODE,
        "page": page,
        "pageSize": page_size,
        "experience": "108",  # 应届生
    }

    headers = {**HEADERS, "Cookie": f"lastCity={CITY_CODE}"}

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(SEARCH_URL, params=params, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                return _parse_jobs(data)
            else:
                print(f"  [Boss] {keyword} 第{page}页 HTTP {resp.status_code}")
                return []
        except Exception as e:
            print(f"  [Boss] {keyword} 请求失败: {e}")
            return []


def _parse_jobs(data: dict) -> list:
    """解析Boss直聘API返回数据"""
    results = []
    job_list = data.get("zpData", {}).get("jobList", []) or data.get("data", {}).get("jobList", [])

    for item in job_list:
        try:
            title = item.get("jobName", "")
            brand_name = item.get("brandName", "")
            salary_desc = item.get("salaryDesc", "") or item.get("salary", "")
            city = item.get("cityName", "") or item.get("city", "")
            education = item.get("degreeName", "") or item.get("education", "") or "本科"
            experience = item.get("workingExp", "") or item.get("experienceName", "") or "应届生"
            desc = item.get("jobDescription", "") or item.get("jobDetail", "") or ""

            if not title:
                continue

            # 解析薪资 "8K-15K"
            salary_min, salary_max = _parse_salary(salary_desc)

            # 推断行业
            industry = _guess_industry(title)

            results.append({
                "title": title,
                "industry": industry,
                "salary_min": salary_min,
                "salary_max": salary_max,
                "education": education,
                "experience": experience,
                "description": desc[:500] if desc else f"{title}岗位{'，欢迎应届毕业生投递' if brand_name else ''}。",
                "source": "Boss直聘",
            })
        except Exception:
            continue

    return results


def _parse_salary(salary_str: str) -> tuple[int, int]:
    """解析薪资字符串 如 '8K-15K' → (8, 15)"""
    if not salary_str:
        return (6, 12)
    # 匹配数字
    nums = re.findall(r"(\d+)", salary_str)
    if len(nums) >= 2:
        return (int(nums[0]), int(nums[1]))
    elif len(nums) == 1:
        n = int(nums[0])
        return (n, n + 5)
    return (6, 12)


def _guess_industry(title: str) -> str:
    """根据岗位名称推断行业"""
    title_lower = title.lower()
    if any(k in title_lower for k in ["python", "java", "前端", "后端", "算法", "测试", "运维", "开发", "数据", "ai"]):
        return "互联网/IT"
    if any(k in title_lower for k in ["产品", "ui", "设计", "运营", "市场", "新媒体", "短视频"]):
        return "互联网/IT"
    if any(k in title_lower for k in ["金融", "投资", "银行", "证券"]):
        return "金融"
    if any(k in title_lower for k in ["制造", "机械", "电气"]):
        return "制造业"
    if any(k in title_lower for k in ["教育", "培训", "讲师"]):
        return "教育/咨询"
    if any(k in title_lower for k in ["电商", "直播"]):
        return "电商/新媒体"
    return "互联网/IT"


async def run_boss(output_file: str = None) -> list:
    """运行Boss直聘爬虫，返回岗位列表"""
    all_jobs = []
    print(f"[Boss直聘] 开始爬取 {len(KEYWORDS)} 个关键词...")

    for kw in KEYWORDS:
        print(f"  搜索: {kw}")
        jobs = await search_jobs(kw, page=1, page_size=10)
        all_jobs.extend(jobs)
        print(f"    获取 {len(jobs)} 条")
        await asyncio.sleep(random.uniform(2.0, 4.0))

    # 去重
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        if job["title"] not in seen:
            seen.add(job["title"])
            unique_jobs.append(job)

    print(f"[Boss直聘] 共获取 {len(unique_jobs)} 条不重复岗位")

    if output_file:
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(unique_jobs, f, ensure_ascii=False, indent=2)
        print(f"[Boss直聘] 数据已保存到 {output_file}")

    return unique_jobs


if __name__ == "__main__":
    asyncio.run(run_boss("data/boss_jobs.json"))

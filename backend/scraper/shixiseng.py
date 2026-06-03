"""
实习僧岗位爬虫
搜索关键词 → 解析岗位列表 → 入库
"""
import asyncio
import httpx
import json
import random
import time
from pathlib import Path

# 浏览器伪装
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://www.shixiseng.com/",
}

# 实习僧搜索 API（移动端接口，反爬较松）
SEARCH_URL = "https://apigw.shixiseng.com/api/v2/search/interns"

# 我们要爬的岗位关键词
KEYWORDS = [
    "Python开发", "前端开发", "数据分析", "Java开发",
    "产品经理", "UI设计", "运营", "算法",
    "测试", "运维", "市场营销", "人力资源",
]


async def search_jobs(keyword: str, page: int = 1, page_size: int = 20) -> list:
    """搜索实习岗位"""
    params = {
        "keyword": keyword,
        "page": page,
        "pageSize": page_size,
        "city": "全国",
    }

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(SEARCH_URL, params=params, headers=HEADERS)
            if resp.status_code == 200:
                data = resp.json()
                return _parse_jobs(data)
            else:
                print(f"  [实习僧] {keyword} 第{page}页 HTTP {resp.status_code}")
                return []
        except Exception as e:
            print(f"  [实习僧] {keyword} 请求失败: {e}")
            return []


def _parse_jobs(data: dict) -> list:
    """解析API返回的岗位数据，转成我们的 job 格式"""
    results = []
    items = data.get("data", {}).get("list", []) or data.get("data", [])

    if isinstance(items, dict):
        items = items.get("list", [])

    for item in items:
        try:
            # 提取字段（适配实际API结构）
            title = item.get("title") or item.get("name") or item.get("jobName", "")
            company = item.get("companyName") or item.get("company_name", "")
            salary_min = item.get("salaryMin") or item.get("salary_min") or 0
            salary_max = item.get("salaryMax") or item.get("salary_max") or 0
            city = item.get("cityName") or item.get("city", "")
            education = item.get("education") or item.get("degree", "") or "本科"
            desc = item.get("description") or item.get("desc") or item.get("jobDetail", "")

            if not title:
                continue

            # 月薪统一为千元
            if salary_max > 100:
                salary_min = salary_min // 1000
                salary_max = salary_max // 1000

            if salary_min == 0:
                salary_min = 3
            if salary_max == 0:
                salary_max = 8

            # 推断行业
            industry = _guess_industry(title)

            results.append({
                "title": title,
                "industry": industry,
                "salary_min": int(salary_min),
                "salary_max": int(salary_max),
                "education": education,
                "experience": "应届生",
                "description": desc[:500] if desc else f"{title}岗位，欢迎优秀应届毕业生投递。",
                "source": "实习僧",
            })
        except Exception:
            continue

    return results


def _guess_industry(title: str) -> str:
    """根据岗位名称推断行业"""
    title_lower = title.lower()
    if any(k in title_lower for k in ["python", "java", "前端", "后端", "算法", "测试", "运维", "开发", "数据", "ai", "技术"]):
        return "互联网/IT"
    if any(k in title_lower for k in ["产品", "ui", "设计", "运营", "市场", "新媒体"]):
        return "互联网/IT"
    if any(k in title_lower for k in ["金融", "投资", "银行", "证券", "保险"]):
        return "金融"
    if any(k in title_lower for k in ["制造", "机械", "电气", "自动化"]):
        return "制造业"
    if any(k in title_lower for k in ["教育", "培训", "讲师", "咨询"]):
        return "教育/咨询"
    if any(k in title_lower for k in ["电商", "直播", "短视频"]):
        return "电商/新媒体"
    return "互联网/IT"


async def run_shixiseng(output_file: str = None) -> list:
    """运行实习僧爬虫，返回岗位列表"""
    all_jobs = []
    print(f"[实习僧] 开始爬取 {len(KEYWORDS)} 个关键词...")

    for kw in KEYWORDS:
        print(f"  搜索: {kw}")
        jobs = await search_jobs(kw, page=1, page_size=10)
        all_jobs.extend(jobs)
        print(f"    获取 {len(jobs)} 条")
        # 礼貌延迟，避免被封
        await asyncio.sleep(random.uniform(1.5, 3.0))

    # 去重
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        if job["title"] not in seen:
            seen.add(job["title"])
            unique_jobs.append(job)

    print(f"[实习僧] 共获取 {len(unique_jobs)} 条不重复岗位")

    if output_file:
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(unique_jobs, f, ensure_ascii=False, indent=2)
        print(f"[实习僧] 数据已保存到 {output_file}")

    return unique_jobs


if __name__ == "__main__":
    asyncio.run(run_shixiseng("data/shixiseng_jobs.json"))

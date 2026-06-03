"""
一键运行所有爬虫 → 导入MySQL
用法: python run_all.py
如果爬虫被反爬拦截，自动使用备用数据
"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper.shixiseng import run_shixiseng
from scraper.boss import run_boss
from scraper.import_to_db import run_import

# 备用数据：如果爬虫失败，用这份高质量Mock数据
FALLBACK_JOBS = [
    # 互联网/IT
    {"title": "Python后端开发实习生", "industry": "互联网/IT", "salary_min": 6, "salary_max": 10, "education": "本科", "experience": "应届生", "description": "参与公司核心业务系统后端开发，负责API设计和数据库优化，与前端团队协作完成产品迭代。"},
    {"title": "前端开发工程师（实习）", "industry": "互联网/IT", "salary_min": 5, "salary_max": 9, "education": "本科", "experience": "应届生", "description": "负责Web前端开发，使用Vue/React框架实现产品界面，优化页面性能和用户体验。"},
    {"title": "数据分析实习生", "industry": "互联网/IT", "salary_min": 5, "salary_max": 8, "education": "本科", "experience": "应届生", "description": "负责业务数据提取分析，撰写数据报告，为产品和运营决策提供数据支持。"},
    {"title": "Java开发工程师（校招）", "industry": "互联网/IT", "salary_min": 8, "salary_max": 15, "education": "本科", "experience": "应届生", "description": "负责大型分布式系统的设计与开发，参与微服务架构演进，编写高质量Java代码。"},
    {"title": "算法工程师实习生", "industry": "互联网/IT", "salary_min": 10, "salary_max": 18, "education": "硕士", "experience": "应届生", "description": "参与推荐系统/自然语言处理算法研发，优化模型效果，跟踪前沿AI技术。"},
    {"title": "产品经理实习生", "industry": "互联网/IT", "salary_min": 5, "salary_max": 9, "education": "本科", "experience": "应届生", "description": "协助产品经理进行需求调研、原型设计和项目跟进，撰写PRD文档。"},
    {"title": "软件测试实习生", "industry": "互联网/IT", "salary_min": 5, "salary_max": 8, "education": "本科", "experience": "应届生", "description": "编写测试用例，执行功能测试和回归测试，使用自动化测试工具提升测试效率。"},
    {"title": "UI设计实习生", "industry": "互联网/IT", "salary_min": 4, "salary_max": 7, "education": "本科", "experience": "应届生", "description": "负责产品界面视觉设计，输出高质量UI稿，参与设计规范制定。"},
    {"title": "新媒体运营实习生", "industry": "电商/新媒体", "salary_min": 4, "salary_max": 7, "education": "本科", "experience": "应届生", "description": "负责公司新媒体账号内容策划和日常运营，提升粉丝活跃度和品牌曝光。"},
    {"title": "短视频运营实习生", "industry": "电商/新媒体", "salary_min": 4, "salary_max": 8, "education": "本科", "experience": "应届生", "description": "负责抖音/快手等平台的短视频内容创作和账号运营，分析数据优化内容策略。"},
    # 金融
    {"title": "金融分析实习生", "industry": "金融", "salary_min": 5, "salary_max": 10, "education": "本科", "experience": "应届生", "description": "协助分析师进行行业研究和公司基本面分析，参与撰写研究报告。"},
    {"title": "量化研究实习生", "industry": "金融", "salary_min": 8, "salary_max": 20, "education": "硕士", "experience": "应届生", "description": "参与量化策略研究与回测，使用Python进行数据分析，优化交易模型。"},
    {"title": "风控数据分析实习生", "industry": "金融", "salary_min": 6, "salary_max": 12, "education": "本科", "experience": "应届生", "description": "负责信贷风控数据分析和模型开发，应用机器学习算法识别风险。"},
    # 制造业
    {"title": "智能制造工程师（实习）", "industry": "制造业", "salary_min": 5, "salary_max": 9, "education": "本科", "experience": "应届生", "description": "参与工厂智能化改造项目，负责自动化设备调试和生产数据采集分析。"},
    {"title": "嵌入式软件开发实习生", "industry": "制造业", "salary_min": 6, "salary_max": 12, "education": "本科", "experience": "应届生", "description": "负责嵌入式系统软件开发和调试，参与IoT设备固件编写。"},
    # 教育/咨询
    {"title": "管理咨询实习生", "industry": "教育/咨询", "salary_min": 6, "salary_max": 12, "education": "本科", "experience": "应届生", "description": "协助咨询顾问进行行业调研、数据分析和报告撰写，参与客户访谈。"},
    {"title": "课程设计实习生", "industry": "教育/咨询", "salary_min": 4, "salary_max": 7, "education": "本科", "experience": "应届生", "description": "参与在线课程内容设计与开发，协助教学资源整理和课程质量评估。"},
    # 电商/新媒体
    {"title": "电商运营实习生", "industry": "电商/新媒体", "salary_min": 4, "salary_max": 7, "education": "本科", "experience": "应届生", "description": "负责淘宝/京东店铺日常运营，策划营销活动，分析销售数据提升转化率。"},
    {"title": "社群运营实习生", "industry": "电商/新媒体", "salary_min": 4, "salary_max": 6, "education": "本科", "experience": "应届生", "description": "负责用户社群的日常运营和维护，策划社群活动提升用户活跃度。"},
    {"title": "市场营销实习生", "industry": "互联网/IT", "salary_min": 4, "salary_max": 8, "education": "本科", "experience": "应届生", "description": "协助市场推广方案策划与执行，跟踪投放效果，进行竞品分析。"},
]


async def main():
    data_dir = Path(__file__).parent.parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    all_jobs = []

    # 尝试爬实习僧
    try:
        print("=" * 50)
        print("[1/2] 爬取实习僧...")
        jobs = await run_shixiseng(str(data_dir / "shixiseng_jobs.json"))
        all_jobs.extend(jobs)
    except Exception as e:
        print(f"  [实习僧] 爬取失败: {e}")

    # 尝试爬Boss直聘
    try:
        print("\n[2/2] 爬取Boss直聘...")
        jobs = await run_boss(str(data_dir / "boss_jobs.json"))
        all_jobs.extend(jobs)
    except Exception as e:
        print(f"  [Boss直聘] 爬取失败: {e}")

    # 如果两个爬虫都没拿到数据，用备用数据
    if len(all_jobs) < 5:
        print(f"\n[!] 爬虫获取数据不足（{len(all_jobs)}条），启用备用数据")
        all_jobs = FALLBACK_JOBS
        with open(data_dir / "fallback_jobs.json", "w", encoding="utf-8") as f:
            json.dump(all_jobs, f, ensure_ascii=False, indent=2)
        print(f"  备用数据 {len(all_jobs)} 条")
    else:
        # 合并去重
        seen = set()
        unique = []
        for j in all_jobs:
            if j["title"] not in seen:
                seen.add(j["title"])
                unique.append(j)
        all_jobs = unique
        with open(data_dir / "all_jobs.json", "w", encoding="utf-8") as f:
            json.dump(all_jobs, f, ensure_ascii=False, indent=2)

    # 导入MySQL
    print("\n[导入] 写入MySQL...")
    await run_import()

    print(f"\n{'=' * 50}")
    print(f"  完成！共 {len(all_jobs)} 条岗位数据")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    asyncio.run(main())

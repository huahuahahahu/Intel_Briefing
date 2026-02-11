import sys
import os
import argparse
import datetime
import json
from fetch_unified_intel import fetch_all_sources, generate_report as generate_v2_report

# Configuration
REPORT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports", "daily_briefings")
SUMMARIES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports", "summaries")

# Import summary generator
LOCAL_SRC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
if LOCAL_SRC_PATH not in sys.path:
    sys.path.insert(0, LOCAL_SRC_PATH)

try:
    from utils.generate_summaries import generate_summaries
    SUMMARIES_AVAILABLE = True
except ImportError as e:
    SUMMARIES_AVAILABLE = False
    print(f"[WARN] Summary generator not available: {e}")

def generate_morning_report(days: int = 1):
    """
    Orchestrate the collection of intelligence using Unified Engine V2.
    Supports Daily (days=1) or Weekly/Custom (days>1) briefings.
    """
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Determine Report Type
    if days == 1:
        report_title = f"每日商业情报简报: {date_str}"
        file_name = f"Morning_Report_{date_str}.md"
        limit = 15
    else:
        report_title = f"周期性情报简报 (过去 {days} 天): {date_str}"
        file_name = f"Weekly_Report_{days}Days_{date_str}.md"
        limit = 30  # Fetch more for weekly
        
    report_file = os.path.join(REPORT_DIR, file_name)
    os.makedirs(REPORT_DIR, exist_ok=True)
    
    print(f"🚀 开始生成情报简报 (Unified V2) - 周期: {days} 天...")
    print(f"   目标文件: {file_name}")
    print(f"   抓取数量: {limit}/源")
    
    # 1. Fetch from all 9 sources
    intel = fetch_all_sources(limit_per_source=limit)
    
    # 2. Generate Report using V2 Renderer
    body = generate_v2_report(intel, date_str)
    
    # Replace the default title with our custom one if needed, or just prepend
    final_content = f"# {report_title}\n\n" + body.replace("# 🌐 全球情报日报 (Global Intel Briefing)", "")
    
    # 3. Save Report
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(final_content)
    
    print(f"\n✅ 简报已生成: {report_file}")
    
    # 4. Generate AI Summaries (pre-bake for PWA)
    if SUMMARIES_AVAILABLE:
        print(f"\n📝 开始生成 AI 摘要...")
        os.makedirs(SUMMARIES_DIR, exist_ok=True)
        
        summaries = generate_summaries(intel, date_str)
        
        if summaries:
            summaries_file = os.path.join(SUMMARIES_DIR, f"{date_str}.json")
            with open(summaries_file, "w", encoding="utf-8") as f:
                json.dump(summaries, f, ensure_ascii=False, indent=2)
            print(f"✅ AI 摘要已保存: {summaries_file} ({len(summaries)} 条)")
        else:
            print("⚠️ 未生成任何摘要")
    else:
        print("\n⚠️ 跳过 AI 摘要生成（模块不可用）")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生成商业情报简报 (Unified V2)")
    parser.add_argument("days", nargs="?", type=int, default=1, help="分析天数 (默认: 1)")
    args = parser.parse_args()
    
    generate_morning_report(days=args.days)


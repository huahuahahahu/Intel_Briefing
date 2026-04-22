"""
Graceful Degradation Tests — 验证缺失 API key 时系统优雅降级，不崩溃。
"""


def test_empty_report_renders():
    """空数据应该产出格式正确的报告，不应崩溃。"""
    from src.report_generator import generate_report
    intel = {k: [] for k in [
        "tech_trends", "capital_flow", "product_gems",
        "community", "research", "social", "insights", "xhs_directives"
    ]}
    report = generate_report(intel, "2026-01-01")
    assert "全球情报日报" in report
    assert report.count("暂无数据") >= 3


def test_report_with_mixed_data():
    """部分有数据部分为空时，报告应正常渲染，不崩溃。"""
    from src.report_generator import generate_report
    intel = {
        "tech_trends": [
            {"title": "Test", "url": "https://example.com", "heat": "10", "time": "1h", "category": "HN"}
        ],
        "capital_flow": [],
        "product_gems": [],
        "community": [],
        "research": [],
        "social": [],
        "insights": [],
        "xhs_directives": [],
    }
    report = generate_report(intel, "2026-01-01")
    assert "Test" in report
    assert "https://example.com" in report
    # Empty sections should show placeholder
    assert "暂无数据" in report

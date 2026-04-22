"""
Anti-Hallucination Tests — 验证防幻觉机制。
核心断言：Grok fallback 产生的猜测 URL 不能作为可点击 markdown 链接进入最终报告。
"""


def test_grok_fallback_not_clickable():
    """Grok 猜测的 PH URL 不应渲染成 markdown 可点击链接。"""
    from src.report_generator import generate_report
    intel = {
        "tech_trends": [], "capital_flow": [], "community": [],
        "research": [], "social": [], "insights": [],
        "xhs_directives": [],
        "product_gems": [{
            "title": "FakeProduct",
            "url": "https://www.producthunt.com/posts/fakeproduct",
            "heat": "100 votes",
            "tagline": "A fake product for testing",
            "topics": ["grok-fallback"],
        }],
    }
    report = generate_report(intel, "2026-01-01")

    # Grok fallback URL 不应作为 markdown 链接出现
    assert "[FakeProduct](https://www.producthunt.com/posts/fakeproduct)" not in report
    # 产品标题应该出现在报告中
    assert "FakeProduct" in report
    # 应该有未验证标记
    assert "未验证" in report


def test_verified_ph_url_is_clickable():
    """正常 PH API 返回的 URL 应正常渲染为 markdown 链接。"""
    from src.report_generator import generate_report
    intel = {
        "tech_trends": [], "capital_flow": [], "community": [],
        "research": [], "social": [], "insights": [],
        "xhs_directives": [],
        "product_gems": [{
            "title": "RealProduct",
            "url": "https://www.producthunt.com/posts/realproduct",
            "heat": "200 votes",
            "tagline": "A real product",
            "topics": ["ai", "developer-tools"],
        }],
    }
    report = generate_report(intel, "2026-01-01")
    assert "[RealProduct](https://www.producthunt.com/posts/realproduct)" in report
    assert "未验证" not in report

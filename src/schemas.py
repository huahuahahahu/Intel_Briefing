"""
Intel Briefing - Unified Data Schemas

Defines the canonical data structures for intelligence items and reports.
Replaces the inconsistent dict schemas across sensors (heat/detail/summary/content drift).

Usage:
    from schemas import IntelItem, BriefingReport
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class IntelItem:
    """A single intelligence item from any sensor.

    This is the canonical schema that all sensors should normalize to.
    Replaces the ad-hoc dicts with inconsistent field names like
    'heat' vs 'votes_count', 'detail' vs 'content' vs 'summary'.
    """

    title: str
    url: str
    source: str              # e.g., "Hacker News", "Product Hunt", "ArXiv"
    category: str            # e.g., "tech_trends", "capital_flow", "research"
    timestamp: str = ""      # ISO-ish string (was: 'time', 'pub_date', 'published')
    heat: str = ""           # Human-readable popularity (was: int, str, or missing)
    summary: str = ""        # Short description (was: 'detail', 'content', 'description', 'tagline')
    author: str = ""         # Creator name
    extra: dict = field(default_factory=dict)  # Sensor-specific data (grok_review, categories, etc.)

    @property
    def is_valid(self) -> bool:
        """Minimum viability check."""
        return bool(self.title and self.url)


@dataclass
class MarkdownReport:
    """A raw markdown report from an AI model (Grok, Gemini).

    Some sensors return freeform markdown instead of structured items.
    This type explicitly models that pattern instead of hiding it in a dict.
    """

    source: str              # e.g., "X (via Grok)"
    content: str             # The markdown text
    report_type: str = ""    # e.g., "horizon_scan", "sentiment_review"


@dataclass
class BriefingReport:
    """The final assembled briefing ready for rendering.

    Aggregates all IntelItems and MarkdownReports into a single output
    that the report generator can consume.
    """

    date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    tech_trends: list[IntelItem] = field(default_factory=list)
    capital_flow: list[IntelItem] = field(default_factory=list)
    product_gems: list[IntelItem] = field(default_factory=list)
    community: list[IntelItem] = field(default_factory=list)
    research: list[IntelItem] = field(default_factory=list)
    insights: list[IntelItem] = field(default_factory=list)
    social_reports: list[MarkdownReport] = field(default_factory=list)

    @property
    def total_items(self) -> int:
        return (
            len(self.tech_trends)
            + len(self.capital_flow)
            + len(self.product_gems)
            + len(self.community)
            + len(self.research)
            + len(self.insights)
            + len(self.social_reports)
        )

    @property
    def summary_line(self) -> str:
        parts = []
        if self.tech_trends:
            parts.append(f"Tech:{len(self.tech_trends)}")
        if self.capital_flow:
            parts.append(f"Capital:{len(self.capital_flow)}")
        if self.product_gems:
            parts.append(f"Products:{len(self.product_gems)}")
        if self.research:
            parts.append(f"Papers:{len(self.research)}")
        if self.insights:
            parts.append(f"Insights:{len(self.insights)}")
        if self.social_reports:
            parts.append(f"Social:{len(self.social_reports)}")
        return f"[{self.date}] {' | '.join(parts)} (Total: {self.total_items})"

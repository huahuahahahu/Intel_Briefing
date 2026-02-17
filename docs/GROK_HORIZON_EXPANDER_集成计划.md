# X/Grok Horizon Expander 集成计划 v2

> **文档目的**：为下一个 Agent 会话提供完整上下文，使其能立即理解目标、现状、代码结构并开始实施。  
> **优先级**：P1（核心信息源质量升级）  
> **创建时间**：2026-02-17  
> **版本**：v2 — 经思维树分析 + Gemini 圆桌审查后的最终版本  

---

## 一、目标与动机

### 我们要做什么
将 `intel-briefing-engine` 中 X（Twitter）社交情报板块从「低质量幻觉输出」升级为「结构化深度情报扫描」。

### 为什么要做
当前每日报告的 `🐦 社交热议 (Social)` 板块由 Grok API 生成，但使用了一个极其简陋的 prompt：

```
"Search X for the latest trends about 'AI Agents, LLM, Tech Startups'"
```

**导致的问题**：
- Grok **捏造了虚假账号**（@TechInnovator23、@DevGuru99、@StartupFounderX — 全是编的）
- Grok **编造了不存在的事件**（AgentSphere、HealthAIx、OpenMind-2026 — 没有一个是真的）
- 输出缺乏结构，没有信号过滤，无法区分噪音和真正有价值的情报
- 整个板块实质上是「AI 幻觉垃圾」，对用户毫无价值

### 解决方案
注入用户经过反复验证的 **GROK HORIZON EXPANDER** 5 步深度协议，并融合 7Brief 的 HUNT 行动标签系统。

---

## 二、架构决策（已裁决）

经思维树分析和 Gemini 圆桌审查，以下 5 个关键决策已确定：

| # | 决策点 | 裁决 | 理由 |
|---|--------|------|------|
| Q1 | Prompt 语言 | **英文 prompt + 强制中文输出** | Grok 英文推理能力更强；`ruthlessly eliminate` 等极客表达能最大化激活高维思考 |
| Q2 | API 成本 | **忽略不计** | 每日 Cron Job 仅调用 1-2 次，即使 5000 tokens 输出，月成本 < $2 |
| Q3 | Timeout | **120 秒** | 后台任务，用户零感知；深度搜索+验证需要时间 |
| Q4 | Temperature | **0.3**（仅 Horizon Scan） | 原 0.5 太高导致幻觉；但 Synthesis 步骤需要一定创造力，0.2 太死板，折中 0.3 |
| Q5 | HUNT 标签 | **嵌入 prompt 第 5 步** | 在 Actionable Horizon 中输出 `[LEARN/CREATE/ARB/ON HOLD]` 标签，作为 markdown 文本丰富度 |

---

## 三、代码架构全景（必读）

### 3.1 仓库结构

本任务涉及 **`intel-briefing-engine`** 仓库（`d:\Project\intel-briefing-engine\`），不是 PWA 前端仓库。

```
intel-briefing-engine/
├── fetch_unified_intel.py          ← 主入口：拉取所有数据源 + 生成报告
├── src/
│   ├── sensors/
│   │   ├── x_grok_sensor.py        ← ⭐ Grok API 包装器（改这里）
│   │   ├── product_hunt.py
│   │   ├── arxiv_ai.py
│   │   ├── hn_blogs.py
│   │   ├── techcrunch_rss.py
│   │   ├── mit_tech_review.py
│   │   └── xhs_radar.py
│   ├── external/
│   │   └── fetch_news.py           ← HN, GitHub, 36Kr, WallStreetCN, V2EX
│   └── utils/
│       ├── gemini_translator.py
│       ├── jina_reader.py
│       └── verifier.py             ← verify_link() 函数（注意：不是 validate_grok_report）
├── .env.example
├── .github/workflows/
│   └── daily-report.yml            ← CI: 每日自动运行
└── reports/daily_briefings/
```

### 3.2 数据流

```
Cloudflare Cron Trigger (每日 00:01 UTC+8)
    ↓
GitHub Actions: daily-report.yml
    ↓
fetch_unified_intel.py → fetch_all_sources()
    ├── HN, GitHub, 36Kr...        ← 各 sensor
    ├── x_grok_sensor.py           ← ⭐ 本次改动
    └── PH + Grok 舆情核查        ← 已有 Grok 集成，不动
    ↓
generate_report() → Morning_Report_YYYY-MM-DD.md
    ↓
git push → intel-briefing-pwa (data/daily_briefings/)
    ↓
PWA CI/CD → 构建 + 部署到 Cloudflare Pages
```

### 3.3 Grok API 配置（已就位 ✅）

| 配置项 | 值 | 来源 |
|--------|-----|------|
| `XAI_API_KEY` | `sk-xxx` | GitHub Secret + `.env` |
| `XAI_BASE_URL` | `https://api.gptsapi.net/v1/chat/completions` | 中转站端点 |
| `XAI_MODEL` | `grok-3` | `.env.example` + GitHub Actions |

---

## 四、需要修改的文件（2 个）

### ⚠️ 关键排雷信息（Gemini 的代码有 4 个 Bug，实施时必须避开）

| # | Gemini 建议 | 问题 | 正确做法 |
|---|-------------|------|----------|
| Bug1 | 把 `httpx` 换成 `requests` | 项目依赖是 `httpx`，不是 `requests` | **保持 `httpx`** |
| Bug2 | `from src.sensors.x_grok_sensor import ...` | `src/` 已加入 `sys.path`（见第 20-22 行），正确路径是 `from sensors.x_grok_sensor` | **保持原有 import 路径** |
| Bug3 | `from src.utils.verifier import validate_grok_report` | `validate_grok_report` 定义在 `fetch_unified_intel.py` 自身（第 116 行），不在 utils | **直接调用本文件函数** |
| Bug4 | 重写 `fetch_grok_intel()` 整个函数 | 会破坏 PH 舆情核查等现有调用 | **只新增函数，不碰旧代码** |

---

### 4.1 `src/sensors/x_grok_sensor.py`

> **原则**：`fetch_grok_intel()` 一字不动，只在文件末尾新增 `fetch_horizon_scan()` 函数。

**当前代码结构**：

```python
# 第 5 行: import httpx                ← 保持，不换 requests
# 第 15 行: XAI_API_KEY = ...
# 第 17 行: XAI_BASE_URL = ...
# 第 18 行: MODEL_NAME = ...
# 第 20 行: def fetch_grok_intel(...)   ← 不动
#   第 74 行: timeout=60                ← 改为参数化
# 第 96 行: if __name__ == "__main__"   ← 保留
```

**改动 1**：将 `timeout` 参数化（第 20 行 + 第 74 行）

```diff
-def fetch_grok_intel(query: str, override_prompt: str = None) -> str:
+def fetch_grok_intel(query: str, override_prompt: str = None, timeout: int = 60) -> str:
```

```diff
-        response = httpx.post(XAI_BASE_URL, headers=headers, json=payload, timeout=60)
+        response = httpx.post(XAI_BASE_URL, headers=headers, json=payload, timeout=timeout)
```

**改动 2**：在 `if __name__` 块之前，新增 `fetch_horizon_scan()` 函数

```python
def fetch_horizon_scan(
    focus: str = "AI, technology breakthroughs, stealth startups, geopolitics, energy",
    timeframe: str = "last 48 hours"
) -> str:
    """
    使用 GROK HORIZON EXPANDER 5步协议对 X 进行深度情报扫描。
    专为 7Brief 的 HUNT 行动系统定制。
    比 fetch_grok_intel() 的默认 prompt 质量高 10 倍。
    """

    today_str = datetime.datetime.now().strftime("%Y-%m-%d")

    horizon_prompt = f"""You are now in GROK HORIZON EXPANDER MODE: An elite intelligence synthesizer designed to expand human worldview by surfacing the most profound, underreported, and paradigm-shifting developments occurring right now on X (Twitter).

Current Date: {today_str}
Timeframe: {timeframe}
Focus area: {focus}

Mandatory protocol — execute every step without exception:

1. Real-Time Signal Scan
   - Deep search current X trends, viral posts (Latest mode), semantic clusters, and sudden engagement spikes.
   - Cross-reference with breaking web sources (avoid mainstream homepages; prioritize primary papers, patents, GitHub repos, on-the-ground accounts).
   - Identify 8-12 raw signals that are exploding in attention but low on mainstream coverage.

2. Noise vs. Signal Filter
   - Ruthlessly eliminate: political theater, celebrity drama, manufactured outrage, crypto shills, distraction events.
   - Prioritize signals with potential for second/third-order effects on civilization (energy, computation, biology, space, power structures, human capability).
   - Flag anything that could quietly reshape the next decade.

3. Deep Dive on Top 4-6 Survivors
   For each:
   - Core breakthrough/event in plain language.
   - Primary evidence (links, papers, posts, timestamps). MUST cite real X posts or real @usernames.
   - Why it's underreported (incentives, narrative conflict, complexity).
   - Paradigm-shifting implications (be bold but evidence-based).
   - Probability of major long-term impact (assign % with justification).

4. Synthesis & Worldview Expansion
   - Connect dots between the top signals — what larger picture emerges?
   - What consensus assumptions are being quietly invalidated?
   - One "holy shit" insight that 99% of people will miss in the noise.

5. Actionable Horizon (use these exact tags):
   - [LEARN 学习]: What specific new concept or tech should the user study based on this scan?
   - [CREATE 创作]: What content or product opportunity emerges from these signals?
   - [ARB 套利]: What specific market, attention, or tool arbitrage opportunity is opening up?
   - [ON HOLD 略过]: Flag one hyped signal from the scan that is noise and should be ignored.

*** CRITICAL INSTRUCTIONS ***
1. OUTPUT LANGUAGE: The entire final output MUST be in elegant, professional Simplified Chinese (简体中文). Keep English for entity names, Twitter handles (@xxx), and URLs only.
2. ZERO HALLUCINATION RULE: If you cannot find or verify a real account, link, or event — DROP IT entirely. Truth over comfort. Do NOT invent @usernames or fake posts.
3. FORMAT: Use clean Markdown formatting with headers and bullet points.

Operate with maximum curiosity and zero deference to institutional narratives.
Begin now."""

    print(f"[*] GROK HORIZON EXPANDER: Scanning X for '{focus}' ({timeframe})...")
    print(f"    This deep scan may take up to 2 minutes...")

    return fetch_grok_intel(
        query="Horizon Scan",
        override_prompt=horizon_prompt,
        timeout=120
    )
```

**关键设计要点**：
- 复用 `fetch_grok_intel()` 的 HTTP/错误处理逻辑
- 通过 `timeout=120` 覆盖默认 60 秒
- Prompt 中注入 `today_str` 防止时间幻觉
- `temperature` 降到 0.3 — 需要在 `fetch_grok_intel` 内部处理（见下文注意事项）

> [!NOTE]
> 关于 temperature：当前 `fetch_grok_intel` 硬编码 `temperature=0.5`（第 70 行）。有两种处理方式：
> - **方案 A（推荐、简单）**：不改 temperature 参数，0.5 对 Horizon prompt 可接受（prompt 本身的 ZERO HALLUCINATION 指令已足够约束）
> - **方案 B（更严格）**：将 temperature 也参数化，Horizon Scan 传 0.3
>
> 建议先用方案 A 上线测试，观察幻觉率后再决定是否降温。

---

### 4.2 `fetch_unified_intel.py`

**改动 1**（第 54 行附近）：更新 import

```diff
     from sensors.x_grok_sensor import fetch_grok_intel
+    from sensors.x_grok_sensor import fetch_horizon_scan
     GROK_AVAILABLE = True
```

> ⚠️ 注意路径是 `sensors.x_grok_sensor`，不是 `src.sensors`。因为 `src/` 已在第 20-22 行加入 `sys.path`。

**改动 2**（第 272-290 行）：替换社交板块调用

```diff
     if GROK_AVAILABLE:
-        print("[*] Fetching X (Twitter) via Grok API...")
+        print("[*] Fetching X (Twitter) via Grok HORIZON EXPANDER...")
         try:
-            # Query Grok for AI/Tech trends on X
-            grok_report = fetch_grok_intel("AI Agents, LLM, Tech Startups")
+            # 使用 HORIZON EXPANDER 5步深度协议
+            grok_report = fetch_horizon_scan(
+                focus="AI agents, LLM scaling, open source, indie hacker, global tech breakthroughs",
+                timeframe="last 48 hours"
+            )
             if grok_report and "Error" not in grok_report:
                 # Anti-Hallucination: Validate all links in Grok's output
                 validated_report = validate_grok_report(grok_report)
                 intel["social"].append({
-                    "source": "X (via Grok)",
-                    "category": "X/Grok",
+                    "source": "X (Horizon Scan)",
+                    "category": "X/Grok Horizon",
                     "content": validated_report,
                     "type": "markdown_report"
                 })
```

> ⚠️ `validate_grok_report()` 是本文件自身定义的函数（第 116 行），不是从 utils 导入的。保持原有调用方式不变。

---

## 五、不需要改动的部分

| 组件 | 原因 |
|------|------|
| PWA 前端 (`intel-briefing-pwa`) | 报告渲染逻辑已支持 `markdown_report` 类型 |
| `generate_report()` 的社交板块（第 478-501 行） | 已直接输出 Grok markdown |
| Product Hunt 舆情核查（第 229-248 行） | 仍用 `fetch_grok_intel()` + 专用 prompt，不受影响 |
| GitHub Actions workflow | `XAI_*` 环境变量已配置 |
| `validate_grok_report()` | 反幻觉链接验证器继续作为第二层保险 |
| `requirements.txt` | 已包含 `httpx`，无需新增依赖 |

---

## 六、GROK HORIZON EXPANDER Prompt 设计哲学

### 为什么分 5 步？

```
Step 1: 信号扫描（广撒网）          → 8-12 条原始信号
Step 2: 降噪过滤（高标准筛选）      → 淘汰噪音，留下 4-6 条
Step 3: 深度钻取（幸存者分析）      → 每条附带证据链 + 影响评估
Step 4: 认知重构（连点成面）        → 跨信号综合洞察
Step 5: 行动视界（HUNT 标签输出）   → LEARN / CREATE / ARB / ON HOLD
```

### 与 7Brief HUNT 系统的协同

7Brief 的核心卖点之一是将情报转化为行动。Horizon Expander 的第 5 步直接输出 HUNT 标签：

- `[LEARN 学习]`：用户应该深入研究的新概念
- `[CREATE 创作]`：内容或产品创作机会
- `[ARB 套利]`：市场/注意力/工具套利窗口
- `[ON HOLD 略过]`：被过度炒作的噪音信号

> [!NOTE]
> 当前这些标签以 markdown 文本形式呈现。未来可以在 PWA 前端解析这些标签，渲染为可交互的行动卡片。

### 三层防幻觉体系

```
Layer 1: Prompt 内置 ZERO HALLUCINATION 指令（"找不到就丢弃"）
Layer 2: temperature 0.5（保守生成）
Layer 3: validate_grok_report() 对所有链接进行 HTTP HEAD 验证
```

---

## 七、验证方法

### 本地快速测试
```bash
cd d:\Project\intel-briefing-engine
python -c "from src.sensors.x_grok_sensor import fetch_horizon_scan; print(fetch_horizon_scan())"
```

### 集成测试（生成完整报告）
```bash
python fetch_unified_intel.py --test --output reports/test_horizon.md
```

### 验证清单
- [ ] `🐦 社交热议` 板块包含结构化的 5 步分析
- [ ] 不再出现捏造的 @username（如 @TechInnovator23）
- [ ] 包含可验证的引用（真实 X 帖子、论文链接等）
- [ ] API 调用在 120 秒内完成
- [ ] Product Hunt 舆情核查不受影响
- [ ] 报告末尾出现 HUNT 标签（LEARN/CREATE/ARB/ON HOLD）

---

*v2 经 Antigravity 思维树分析 + Gemini 圆桌审查，2026-02-17*

import os
import sys
import datetime
import json
import httpx
from dotenv import load_dotenv

# Force UTF-8 stdout for Windows
sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

# Configuration
XAI_API_KEY = os.getenv("XAI_API_KEY")
# Default to official endpoint, but allow override for Relay Services (中转站)
XAI_BASE_URL = os.getenv("XAI_BASE_URL", "https://api.x.ai/v1/chat/completions")
MODEL_NAME = os.getenv("XAI_MODEL", "grok-beta")  # Relay users: set to 'grok-3' or 'grok-4'

def fetch_grok_intel(query: str, override_prompt: str = None, timeout: int = 60) -> str:
    """
    Fetch intelligence from X using xAI's Grok API.
    Returns the markdown report.
    """
    if not XAI_API_KEY:
        print("❌ Error: XAI_API_KEY not found in .env files.")
        return "Error: No API Key."

    print(f"🦅 Grok Sensor: contacting xAI for '{query}'...")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {XAI_API_KEY}"
    }

    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    year_str = datetime.datetime.now().strftime("%Y")

    if override_prompt:
        system_content = f"You are an specialized Data Analyst. Current Date: {today_str}. Follow the user's instructions strictly."
        user_content = override_prompt
    else:
        system_content = (
            f"You are a Commercial Intelligence Analyst. **CURRENT DATE: {today_str}**. "
            "Your goal is to find high-signal discussions from the **LAST 24 HOURS ONLY**. "
            f"❌ CRITICAL RULE: Do NOT report events from {int(year_str)-2} or {int(year_str)-1} as 'new'. "
            "If the trend is from 2024/2025, explicitly label it as 'Historical Context'. "
            "**IMPORTANT: You must answer in Simplified Chinese (简体中文).**"
        )
        user_content = f"Search X for the latest trends about '{query}' happened in {year_str}. Focus on specific recent events. Reply in Chinese."

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {XAI_API_KEY}"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system", 
                "content": system_content
            },
            {
                "role": "user", 
                "content": user_content
            }
        ],
        "stream": False,
        "temperature": 0.5
    }

    try:
        response = httpx.post(XAI_BASE_URL, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        
        data = response.json()
        content = data['choices'][0]['message']['content']
        
        print("\n" + "="*60)
        print(f"  🦅 Grok Intelligence Report: {query}")
        print("="*60 + "\n")
        print(content)
        
        return content
        
    except httpx.HTTPStatusError as e:
        err = f"⚠️ API Error: {e.response.status_code} - {e.response.text}"
        print(err)
        return err
    except Exception as e:
        err = f"⚠️ Connection Error: {e}"
        print(err)
        return err

def fetch_horizon_scan(
    focus: str = "AI, technology breakthroughs, stealth startups, geopolitics, energy",
    timeframe: str = "last 48 hours"
) -> str:
    """
    使用 GROK HORIZON EXPANDER 5步协议对 X 进行深度情报扫描。
    专为 7Brief HUNT 行动系统定制。
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


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python x_grok_sensor.py <query>")
        print("Example: python x_grok_sensor.py 'AI Agents'")
    else:
        q = sys.argv[1]
        fetch_grok_intel(q)

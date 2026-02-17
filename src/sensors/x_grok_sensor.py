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

    horizon_prompt = f"""As a technology intelligence analyst, please conduct a comprehensive scan of current discussions on X (Twitter) and provide a structured intelligence briefing.

Current Date: {today_str}
Timeframe: {timeframe}
Focus area: {focus}

Please follow this 5-step analytical framework:

1. Signal Scan
   Search X for the most significant recent discussions, viral posts, and emerging trends within the focus area and timeframe above. Cross-reference with primary sources (research papers, GitHub repos, official announcements). Identify 8-12 noteworthy signals that have high engagement but limited mainstream media coverage.

2. Signal Quality Filter
   From the signals above, filter out noise (celebrity gossip, political drama, speculative hype without substance, crypto pump schemes). Keep only signals with genuine potential for long-term, second-order effects on technology, energy, biology, space, or power structures. Narrow down to the top 4-6 highest-quality signals.

3. Deep Analysis of Top Signals
   For each surviving signal, provide:
   - A plain-language summary of the core development
   - Primary evidence: cite real X posts with @usernames and timestamps, or link to real papers/repos
   - Why this is underreported by mainstream sources
   - Potential paradigm-shifting implications
   - Your estimated probability of major long-term impact (with brief justification)

4. Cross-Signal Synthesis
   - What larger pattern or trend connects these top signals?
   - What widely-held assumptions are these signals quietly challenging?
   - Identify one key non-obvious insight that most observers would miss

5. Actionable Recommendations (please use these exact label formats):
   - [LEARN 学习]: One specific concept or technology the reader should study deeper
   - [CREATE 创作]: One content or product opportunity that emerges from these signals
   - [ARB 套利]: One specific market, attention, or tooling arbitrage opportunity
   - [ON HOLD 略过]: One currently hyped signal that is actually noise and should be ignored

Important requirements:
- Write the entire output in professional Simplified Chinese (简体中文). Keep English only for proper nouns, @handles, and URLs.
- Accuracy is paramount: only cite real, verifiable accounts and posts. If you cannot verify something, omit it rather than guessing.
- Use clean Markdown formatting with headers and bullet points."""

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

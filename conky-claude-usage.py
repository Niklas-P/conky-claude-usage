#!/usr/bin/env python3
"""
Claude Code usage widget for Conky.
Fetches 5-hour and 7-day utilization from the Anthropic OAuth usage endpoint.
Results are cached for CACHE_TTL seconds to avoid hammering the API.
Output is Conky markup (parsed via ${execpi}).
"""

import json, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

CREDS_FILE  = Path.home() / ".claude/.credentials.json"
CACHE_FILE  = Path("/tmp/claude-usage-cache.json")
CACHE_TTL   = 300   # seconds between real API calls
API_URL     = "https://api.anthropic.com/api/oauth/usage"
BETA_HEADER = "oauth-2025-04-20"


# ── helpers ──────────────────────────────────────────────────────────────────

def get_token() -> str | None:
    try:
        with open(CREDS_FILE) as f:
            d = json.load(f)
        token = d["claudeAiOauth"]["accessToken"]
        expires_at_ms = d["claudeAiOauth"].get("expiresAt", 0)
        if time.time() * 1000 > expires_at_ms:
            return None   # expired — user needs to run `claude` once to refresh
        return token
    except Exception:
        return None


def fetch_usage(token: str) -> dict | None:
    req = urllib.request.Request(
        API_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "anthropic-beta": BETA_HEADER,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def get_data() -> dict | None:
    if CACHE_FILE.exists():
        age = time.time() - CACHE_FILE.stat().st_mtime
        if age < CACHE_TTL:
            try:
                with open(CACHE_FILE) as f:
                    return json.load(f)
            except Exception:
                pass

    token = get_token()
    if not token:
        return None

    data = fetch_usage(token)
    if data:
        with open(CACHE_FILE, "w") as f:
            json.dump(data, f)
    return data


def format_reset(resets_at: str) -> str:
    try:
        reset_time = datetime.fromisoformat(resets_at)
        now = datetime.now(timezone.utc)
        diff = reset_time - now
        total_s = int(diff.total_seconds())
        if total_s <= 0:
            return "resetting..."
        d = total_s // 86400
        h = (total_s % 86400) // 3600
        m = (total_s % 3600) // 60
        if d > 0:
            return f"{d}d {h}h"
        if h > 0:
            return f"{h}h {m}m"
        return f"{m}m"
    except Exception:
        return "N/A"


def bar(pct: float, width: int = 16) -> str:
    filled = int(width * min(max(pct, 0), 100) / 100)
    return "█" * filled + "░" * (width - filled)


def usage_color(pct: float) -> str:
    if pct >= 90:
        return "#FF5555"
    if pct >= 70:
        return "#FFAA44"
    if pct >= 50:
        return "#FFDD55"
    return "#55CC77"


# ── main ─────────────────────────────────────────────────────────────────────

data = get_data()

if not data:
    token = get_token()
    if token is None:
        msg = "token expired — run claude once"
    else:
        msg = "fetch failed — check network"
    print(f"${{color #FF5555}}Claude: {msg}${{color}}")
    sys.exit(0)

fh = data.get("five_hour", {})
wk = data.get("seven_day", {})

fh_pct   = float(fh.get("utilization", 0))
wk_pct   = float(wk.get("utilization", 0))
fh_reset = format_reset(fh.get("resets_at", ""))
wk_reset = format_reset(wk.get("resets_at", ""))

fh_col = usage_color(fh_pct)
wk_col = usage_color(wk_pct)

SEP = "${color #333333}" + "─" * 24 + "${color}"

lines = [
    "${color #CCCCCC}CLAUDE CODE  USAGE${color}",
    SEP,
    f"${{color #888888}}5h   ${{color {fh_col}}}{bar(fh_pct)} {fh_pct:5.1f}%${{color}}",
    f"${{color #444444}}     resets in {fh_reset}${{color}}",
    "",
    f"${{color #888888}}7d   ${{color {wk_col}}}{bar(wk_pct)} {wk_pct:5.1f}%${{color}}",
    f"${{color #444444}}     resets in {wk_reset}${{color}}",
]

print("\n".join(lines))

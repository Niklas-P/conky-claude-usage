# conky-claude-usage

A lightweight [Conky](https://github.com/brndnmtthws/conky) desktop widget that shows your **Claude Code usage** in real time — 5-hour session window and 7-day weekly window — with color-coded progress bars and countdown timers to the next reset.

![Widget preview](.preview.png)

---

## What it looks like

```
CLAUDE CODE  USAGE
────────────────────────
5h   ██████████████░░  92.0%
     resets in 1h 33m

7d   ██████████░░░░░░  63.0%
     resets in 20h 37m
```

Colors shift automatically based on utilization:

| Usage   | Color  |
|---------|--------|
| < 50 %  | Green  |
| 50–70 % | Yellow |
| 70–90 % | Orange |
| ≥ 90 %  | Red    |

---

## How it works

Claude Code (Max/Pro plan) enforces two rolling usage windows. This widget fetches utilization data from the Anthropic OAuth usage endpoint:

```
GET https://api.anthropic.com/api/oauth/usage
Authorization: Bearer <oauth_access_token>
anthropic-beta: oauth-2025-04-20
```

The OAuth access token is read directly from `~/.claude/.credentials.json`, which Claude Code manages automatically. API results are **cached for 5 minutes** in `/tmp/claude-usage-cache.json` so the endpoint isn't hammered on every Conky tick.

---

## Requirements

- [Conky](https://github.com/brndnmtthws/conky) ≥ 1.10
- Python 3.9+
- Claude Code installed and authenticated (Max or Pro plan)
- A font that renders Unicode block characters (`█ ░`) — **Ubuntu Mono** recommended

---

## Install

### Option A — installer script

```bash
git clone https://github.com/Niklas-P/conky-claude-usage.git
cd conky-claude-usage
bash install.sh
```

### Option B — manual

```bash
# 1. Copy the fetch script
install -D -m 755 conky-claude-usage.py ~/.claude/conky-claude-usage.py

# 2. Copy the Conky config
mkdir -p ~/.conky/claude-usage
cp conkyrc ~/.conky/claude-usage/conkyrc
```

---

## Launch

```bash
conky -c ~/.conky/claude-usage/conkyrc --daemonize
```

### Autostart

Add to your Conky startup script (e.g. `~/.conky/conky-startup.sh`):

```bash
conky -c ~/.conky/claude-usage/conkyrc --daemonize
```

---

## Configuration

Edit `~/.conky/claude-usage/conkyrc` to reposition the widget:

```lua
alignment = 'bottom_right',   -- top_left, top_right, bottom_left, bottom_right
gap_x     = 20,               -- horizontal gap from edge (px)
gap_y     = 20,               -- vertical gap from edge (px)
```

The background opacity is set via `own_window_argb_value` (0 = fully transparent, 255 = opaque).

---

## Notes

- If the widget shows `token expired`, open Claude Code once — it refreshes the OAuth token automatically.
- This endpoint is undocumented and may change. The widget will show an error rather than crash if the API is unreachable.
- Anthropic has no public endpoint for pay-per-use API credit balance; the 5h/7d windows shown here are the Max/Pro plan equivalent.

---

## License

MIT

---
name: ha-morning-brief
description: Morning house brief — live status, overnight anomalies, energy snapshot, pending proposals, and today's priorities. Runs as a daily routine or on demand.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - mcp__homeassistant__GetLiveContext
  - mcp__homeassistant__GetDateTime
  - mcp__plugin_discord_discord__reply
  - mcp__plugin_discord_discord__fetch_messages
---

# HA Morning Brief

A house-focused morning brief that combines live HA state with hermit session context. Designed to run as the `morning` routine at start of day.

## Steps

1. **Time & context** — Call `GetDateTime` for current time. Read `.claude-code-hermit/OPERATOR.md` for priorities and language preferences.

2. **Live house snapshot** — Call `GetLiveContext`. Extract and organize:
   - Presence (who is home/away)
   - Lights still on (unexpected at morning time?)
   - Cover/blind positions
   - Climate: indoor temps, HVAC mode
   - Any devices unavailable or in error state
   - Security: alarm state (read-only)

3. **Energy snapshot** — From the live context, pull current power draw and any energy sensors. Compare with known baselines from memory if available. Flag anything unusual (e.g., high overnight consumption).

4. **Context freshness** — Check `.claude-code-hermit/raw/snapshot-ha-context-latest.json` modification time. If older than 24h, note it as stale.

5. **Overnight activity** — Read the last 10 lines of `.claude-code-hermit/sessions/SHELL.md` Monitoring section for any overnight alerts or findings worth surfacing.

6. **Pending work** — Scan for:
   - `Glob` for `.claude-code-hermit/proposals/PROP-*.md` — read status from each, list any `pending` proposals
   - Check if `.claude-code-hermit/sessions/NEXT-TASK.md` exists (queued task)
   - Read `.claude-code-hermit/cost-summary.md` if it exists — include yesterday's cost

7. **Compose brief** — Write a concise morning brief in the operator's language (from OPERATOR.md preferences). Use the format below.

## Output Format

```
Bom dia! Casa - [date]

Estado actual:
- [presence, lights, climate, covers - concise bullets]

Energia:
- [current draw, overnight highlights]

Alertas:
- [devices offline, unusual states, or "Tudo normal"]

Pendente:
- [proposals, queued tasks, or "Nada pendente"]

Prioridades hoje:
- [from OPERATOR.md Current Priority, filtered to actionable items]
```

Adapt the greeting and section headers to the operator's configured language. Keep the entire brief under 20 lines.

## Delivery

- If invoked from a Discord channel context: send via `reply` to that channel
- If invoked as a routine (no channel context): output to terminal only
- Never include secrets, tokens, or internal file paths in the brief

---
name: ha-hatch
description: One-time Home Assistant setup for this hermit. Configures HA access, connects to the official Home Assistant MCP Server integration, and verifies both the Python CLI and HA MCP. Run once per project after /claude-code-hermit:hatch.
---

# Home Assistant Hatch

Set up the Home Assistant layer for this project. Idempotent — safe to re-run; will skip completed steps and offer re-verify only.

## Plan

### 1. Prereq check

Read `.claude-code-hermit/config.json`.

- If the file is missing or `_hermit_versions["claude-code-hermit"]` is absent or less than `1.0.12`:
  - `AskUserQuestion`: "Core hermit is not initialized. Run `/claude-code-hermit:hatch` now?"
  - Yes → invoke `/claude-code-hermit:hatch`, then continue.
  - No → stop and explain what is required.

### 2. Idempotency check

Read `_hermit_versions["claude-code-homeassistant-hermit"]` from `config.json`. Read the `version` field from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`.

- If versions match → `AskUserQuestion`: "Already set up. Re-verify HA access only (skip setup wizard)?". Yes → skip to §6. No → continue.
- If stale or absent → continue with setup.

### 3. Verify .env

Check that `.env` exists at the project root and contains `HOMEASSISTANT_TOKEN` and `HOMEASSISTANT_LOCAL_URL`.

- **If `.env` is missing or incomplete**:
  1. Tell the user:
     ```
     .env is missing or incomplete. Please create it at the project root:

       cp .env.example .env

     Then fill in:
       HOMEASSISTANT_LOCAL_URL=http://homeassistant.local:8123
       HOMEASSISTANT_TOKEN=<your long-lived access token>

     Long-Lived Access Tokens: Home Assistant → Profile → Long-Lived Access Tokens.
     ```
  2. `AskUserQuestion`: "When your `.env` is ready, type **done** to continue (or **abort** to stop)."
     - **done** → re-check `.env`. If still missing/incomplete, repeat from step 1. If valid, proceed.
     - **abort** → stop.
  Do not write or modify `.env` — it is the user's responsibility.

- **If `.env` is present and has both required keys**: proceed.

Also check locale:

- Read `MEMORY.md`. If a `Language` / locale entry already exists in the House Profile section, use it silently — do not re-ask.
- If absent, ask: **Language / locale**: What language should the agent use for HA-facing output? (e.g. `en`, `pt`, `es`) Store it in `MEMORY.md` House Profile (create the section if missing).

Do not collect or store the token — it stays in `.env` only.

### 4. Python runtime deps + CLI check

Run `python3 -c "import yaml, dotenv"` (or `.venv/bin/python -c "import yaml, dotenv"` if `.venv/` exists).

- **If it passes** → skip to the CLI status check below.
- **If it fails**:
  1. Probe `python3 -m venv --help`. If that fails, stop and tell the user: `apt install python3-venv` (or OS equivalent), then re-run ha-hatch.
  2. `AskUserQuestion`: "Install Python deps into a project-local `.venv`? Recommended — isolates from system Python and works on PEP 668 hosts." Options: `venv` (default) / `system` / `skip`.
     - **`venv`**: run `python3 -m venv ${CLAUDE_PLUGIN_ROOT}/.venv` then `${CLAUDE_PLUGIN_ROOT}/.venv/bin/pip install PyYAML python-dotenv`. Re-probe — if still failing, stop with a diagnostic.
     - **`system`**: run `pip install --user PyYAML python-dotenv`. If it errors with `externally-managed-environment` (PEP 668), offer to fall back to `venv` automatically.
     - **`skip`**: note that §6 will probe again and will fail if deps are absent; continue anyway.
  3. **Do not exit or ask the user to re-run the skill** — continue to the CLI status check in-flight.

CLI check: run `${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab boot status` (read-only, no `--probe`) to confirm the launcher and Python package resolve correctly.

### 5. Home Assistant MCP Server setup

**Step A — Enable the integration in Home Assistant**

Tell the user: go to Home Assistant → Settings → Devices & Services → Add Integration → search "Model Context Protocol Server". Enable it. This exposes the MCP endpoint at `<HOMEASSISTANT_LOCAL_URL>/api/mcp`.

Reference: https://www.home-assistant.io/integrations/mcp_server/

**Step B — Write `.mcp.json`**

Check the project root for `.mcp.json`:
- If absent → write it with the following content. This uses env-var interpolation so the token stays in `.env` and is never stored in the file.
- If present → read it. If it already contains a `homeassistant` key under `mcpServers`, skip. Otherwise merge `homeassistant` into the existing `mcpServers` object without overwriting other entries.

```json
{
  "mcpServers": {
    "homeassistant": {
      "type": "http",
      "url": "${HOMEASSISTANT_LOCAL_URL}/api/mcp",
      "headers": { "Authorization": "Bearer ${HOMEASSISTANT_TOKEN}" }
    }
  }
}
```

The name `homeassistant` is required — skills and the safety hook match on `mcp__homeassistant__*` tool IDs.

Note: `.mcp.json` contains no secrets (values are `${VAR}` references) and is safe to commit if teammates should inherit the registration.

**Step C — Activate and verify**

Tell the user: **restart Claude Code** in this project directory. On first use, Claude Code will prompt you to trust the `homeassistant` server — approve it. Then run `/mcp` to confirm `homeassistant` appears as connected. The next `ha-boot` will verify live HA connectivity.

Alternative: if you prefer user-scope registration (available outside this project), you can run `claude mcp add-json homeassistant '{"type":"http","url":"<url>/api/mcp","headers":{"Authorization":"Bearer <token>"}}'` instead and skip the `.mcp.json` file.

### 6. Verify Python CLI (full probe)

Run `${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab boot status --probe` and present the result. If it fails:

- Missing deps → repeat the §4 venv install steps inline (create `.venv`, pip install) without exiting or re-invoking ha-hatch.
- Connection refused → check `HOMEASSISTANT_LOCAL_URL` in `.env`.
- Auth error → check `HOMEASSISTANT_TOKEN`.

### 7. Append to CLAUDE.md

Read `${CLAUDE_PLUGIN_ROOT}/state-templates/CLAUDE-APPEND.md`.

Check CLAUDE.md for the marker comment `<!-- claude-code-homeassistant-hermit: Home Assistant Workflow -->`:

- Absent → append the full CLAUDE-APPEND.md content.
- Present and version matches current plugin version → skip.
- Present and version is stale → replace the block between the opening and closing markers with the updated content.

### 8. Stamp version and register routines

Write `_hermit_versions["claude-code-homeassistant-hermit"]` into `.claude-code-hermit/config.json` with the current plugin version.

**Reflect routine check**: Read `config.routines` array. If no entry has `"id": "reflect"`, warn:

> "No `reflect` routine found in config.json. Run `/claude-code-hermit:hermit-evolve` to seed it (required for daily pattern tracking in hermit ≥ 1.0.13)."

**HA routine registration**: `config.routines` is an array of objects with `{id, schedule, skill, enabled, run_during_waiting}`. For each HA routine below, check whether an entry with that `id` already exists in the array. If it does, skip. If not, prompt and merge it in.

1. **Context refresh** — "Add daily HA context-refresh routine (08:30 every day)? Keeps entity snapshots fresh automatically."
   ```json
   {"id": "daily-ha-context", "schedule": "30 8 * * *", "skill": "claude-code-homeassistant-hermit:ha-refresh-context", "enabled": true, "run_during_waiting": false}
   ```

2. **Morning brief** — "Add morning house brief routine (09:00 every day)? Delivers a live house summary at start of day. Disabled by default — enable after setup is complete."
   ```json
   {"id": "morning-brief", "schedule": "0 9 * * *", "skill": "claude-code-homeassistant-hermit:ha-morning-brief", "enabled": false, "run_during_waiting": false}
   ```

After adding any new entries, remind the operator: "Run `/claude-code-hermit:hermit-routines load` to activate routines in the current session."

**Plugin checks registration**: `config.plugin_checks` is an array of periodic skill entries that reflect invokes on a cadence and funnels through the proposal pipeline. For each entry below, check whether an existing record has the same `id`. If not, append it — no prompt needed, all four are safe read-only analyses.

```json
{"id": "ha-patterns",            "plugin": "claude-code-homeassistant-hermit", "skill": "claude-code-homeassistant-hermit:ha-analyze-patterns",        "enabled": true, "trigger": "interval", "interval_days": 7}
{"id": "ha-safety-audit",        "plugin": "claude-code-homeassistant-hermit", "skill": "claude-code-homeassistant-hermit:ha-safety-audit",           "enabled": true, "trigger": "interval", "interval_days": 7}
{"id": "ha-integration-health",  "plugin": "claude-code-homeassistant-hermit", "skill": "claude-code-homeassistant-hermit:ha-integration-health",    "enabled": true, "trigger": "interval", "interval_days": 1}
{"id": "ha-automation-errors",   "plugin": "claude-code-homeassistant-hermit", "skill": "claude-code-homeassistant-hermit:ha-automation-error-review", "enabled": true, "trigger": "interval", "interval_days": 1}
```

These replace any need for CronCreate routines around analysis/observability — reflect picks up whichever check is due, runs it, and any findings surface as proposals automatically.

### 9. Final report

Summarize:

```
ha-hatch complete
  ✓  .env verified (user-managed)
  ✓  Python deps: <venv at .venv/ | system python> → OK / FAILED
  ✓  Python CLI: bin/ha-agent-lab boot status --probe → OK / FAILED
  ✓  .mcp.json: homeassistant entry written / already present
  ✓  CLAUDE.md updated
  ✓  config.json stamped v<version>
  ✓  Routines registered: daily-ha-context, morning-brief (disabled by default)
  ✓  plugin_checks registered: ha-patterns, ha-safety-audit, ha-integration-health, ha-automation-errors

Manual steps remaining:
  - Enable 'Model Context Protocol Server' integration in Home Assistant (if not done)
    Settings → Devices & Services → Add Integration → search "MCP"
  - Restart Claude Code and approve the 'homeassistant' server on first use
  - Run /mcp to confirm 'homeassistant' is connected
  - Run /claude-code-homeassistant-hermit:ha-refresh-context to populate the initial context snapshot
  - Run /claude-code-hermit:hermit-routines load to activate scheduled routines in this session
  - Enable `morning-brief` routine in `.claude-code-hermit/config.json` once the house profile is confirmed

Always-on runtime (pick one):
  - Docker (recommended): /claude-code-hermit:docker-setup
  - Direct:               /claude-code-hermit:channel-setup  (if not using Docker)
```
